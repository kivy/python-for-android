
import os
import re
import shutil
import subprocess

import hashlib
import platform
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info


class LibCloudflaredRecipe(Recipe):

    version = "1.4.0"
    url = None
    depends = ["pyjnius"]

    GO_VERSION = "1.27.4"

    GO_RELEASES = {
        ("linux", "x86_64"): {
            "archive": "go1.27.4.linux-amd64.tar.gz",
            "sha256": "7226736c2339719cda28fbf3a54d71aa63bcefe376e98cef00034268dab24840",
        },
        ("linux", "aarch64"): {
            "archive": "go1.27.4.linux-arm64.tar.gz",
            "sha256": "3392582988a273a87ab5043ee1b2c9c17a2c3c00580bf9326c47a2e0aaaeac92",
        },
    }

    def ensure_go(self):

        # Persistent cache shared by Buildozer builds.
        buildozer_home = Path(
            os.environ.get(
                "BUILDOZER_HOME",
                str(Path.home() / ".buildozer")
            )
        )

        go_cache = buildozer_home / "tools" / "go"
        download_cache = go_cache / "downloads"

        host = (
            platform.system().lower(),
            platform.machine().lower()
        )

        release = self.GO_RELEASES.get(host)

        if not release:
            raise RuntimeError(
                f"Unsupported Go host platform: {host}"
            )

        archive_name = release["archive"]
        expected_sha = release["sha256"]

        install_dir = go_cache / f"go{self.GO_VERSION}"
        go_bin = install_dir / "bin" / "go"

        # Reuse existing installation.
        if go_bin.is_file():

            result = subprocess.run(
                [str(go_bin), "version"],
                capture_output=True,
                text=True
            )

            if (
                result.returncode == 0
                and f"go{self.GO_VERSION}" in result.stdout
            ):
                info(f"Using cached Go: {result.stdout.strip()}")
                return str(go_bin)

        download_cache.mkdir(parents=True, exist_ok=True)

        archive_path = download_cache / archive_name

        download_url = (
            f"https://go.dev/dl/{archive_name}"
        )

        # Download only when archive is missing or corrupted.
        valid_archive = False

        if archive_path.is_file():
            digest = hashlib.sha256(
                archive_path.read_bytes()
            ).hexdigest()

            valid_archive = digest == expected_sha

        if not valid_archive:

            info(f"Downloading Go {self.GO_VERSION}")

            temporary_archive = archive_path.with_suffix(
                ".tmp"
            )

            urllib.request.urlretrieve(
                download_url,
                temporary_archive
            )

            digest = hashlib.sha256(
                temporary_archive.read_bytes()
            ).hexdigest()

            if digest != expected_sha:
                temporary_archive.unlink(missing_ok=True)

                raise RuntimeError(
                    "Go archive SHA256 verification failed"
                )

            os.replace(temporary_archive, archive_path)

        # Extract into a temporary directory first.
        go_cache.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(
            dir=go_cache
        ) as temp_dir:

            with tarfile.open(
                archive_path, "r:gz"
            ) as tar:

                # Reject unsafe archive paths.
                for member in tar.getmembers():
                    target = Path(temp_dir) / member.name

                    if not target.resolve().is_relative_to(
                        Path(temp_dir).resolve()
                    ):
                        raise RuntimeError(
                            f"Unsafe Go archive path: {member.name}"
                        )

                tar.extractall(temp_dir)

            extracted_go = Path(temp_dir) / "go"

            if not (extracted_go / "bin" / "go").is_file():
                raise RuntimeError(
                    "Invalid Go archive: missing bin/go"
                )

            if install_dir.exists():
                shutil.rmtree(install_dir)

            shutil.move(
                str(extracted_go),
                str(install_dir)
            )

        # Final verification.
        result = subprocess.run(
            [str(go_bin), "version"],
            capture_output=True,
            text=True,
            check=True
        )

        info(f"Go installed: {result.stdout.strip()}")

        return str(go_bin)


    def build_arch(self, arch):
        super().build_arch(arch)

        # go = self.check_go()
        go = self.ensure_go()
        go_root = str(Path(go).parent.parent)

        if arch.arch != "arm64-v8a":
            raise RuntimeError(
                f"Cloudflared currently supports only arm64-v8a, "
                f"got {arch.arch}"
            )

        ndk = self.ctx.ndk_dir
        api = str(self.ctx.ndk_api)

        host_tag = platform.system().lower() + "-" + platform.machine().lower()
        if not host_tag:
            raise RuntimeError("Unable to determine NDK host tag")

        toolchain = os.path.join(
            ndk, "toolchains", "llvm",
            "prebuilt", host_tag, "bin"
        )

        cc = os.path.join(
            toolchain,
            f"aarch64-linux-android{api}-clang"
        )

        cxx = os.path.join(
            toolchain,
            f"aarch64-linux-android{api}-clang++"
        )

        if not os.path.isfile(cc):
            raise RuntimeError(f"NDK compiler not found: {cc}")

        if not os.path.isfile(cxx):
            raise RuntimeError(f"NDK C++ compiler not found: {cxx}")

        build_dir = self.get_build_dir(arch.arch)
        os.makedirs(build_dir, exist_ok=True)

        source_dir = os.path.join(build_dir, "cloudflared")

        if not os.path.isdir(source_dir):
            info("Cloning Cloudflare cloudflared")

            subprocess.run(
                [
                    "git", "clone",
                    "--depth", "1",
                    "https://github.com/cloudflare/cloudflared.git",
                    source_dir
                ],
                check=True
            )

        recipe_dir = self.get_recipe_dir()
        build_script = os.path.join(recipe_dir, "build.sh")

        if not os.path.isfile(build_script):
            raise RuntimeError(
                f"Missing build script: {build_script}"
            )

        env = os.environ.copy()

        env.update({
            "GO": go,
            "GOROOT": go_root,
            "PATH": str(Path(go).parent) + os.pathsep + env.get("PATH", ""),

            "GOTOOLCHAIN": "local",

            "CC": cc,
            "CXX": cxx,
            "GOOS": "android",
            "GOARCH": "arm64",
            "CGO_ENABLED": "1",
            "ANDROID_NDK": ndk,
            "ANDROID_API": api,
        })

        info("Building cloudflared for Android arm64-v8a")

        subprocess.run(
            ["sh", build_script],
            cwd=source_dir,
            env=env,
            check=True
        )

        output = os.path.join(
            source_dir, "libs", "aarch64",
            "cloudflared-arm64"
        )

        if not os.path.isfile(output):
            raise RuntimeError(
                f"Cloudflared output not found: {output}"
            )

        # p4a automatically packages libraries from this directory.
        destination_dir = self.ctx.get_libs_dir(arch.arch)
        os.makedirs(destination_dir, exist_ok=True)

        destination = os.path.join(
            destination_dir, "libcloudflared.so"
        )

        shutil.copy2(output, destination)
        os.chmod(destination, 0o755)

        info(f"Installed cloudflared: {destination}")


recipe = LibCloudflaredRecipe()