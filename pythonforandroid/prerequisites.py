#!/usr/bin/env python3

import sys
import platform
import os
import subprocess
from pythonforandroid.logger import info, warning, error


class Prerequisite(object):
    name = "Default"
    mandatory = True
    darwin_installer_is_supported = False
    linux_installer_is_supported = False

    def is_valid(self):
        if self.checker():
            info(f"Prerequisite {self.name} is met")
            return (True, "")
        elif not self.mandatory:
            warning(
                f"Prerequisite {self.name} is not met, but is marked as non-mandatory"
            )
        else:
            error(f"Prerequisite {self.name} is not met")

    def checker(self):
        if sys.platform == "darwin":
            return self.darwin_checker()
        elif sys.platform == "linux":
            return self.linux_checker()
        else:
            raise Exception("Unsupported platform")

    def ask_to_install(self):
        if (
            os.environ.get("PYTHONFORANDROID_PREREQUISITES_INSTALL_INTERACTIVE", "1")
            == "1"
        ):
            res = input(
                f"Do you want automatically install prerequisite {self.name}? [y/N] "
            )
            if res.lower() == "y":
                return True
            else:
                return False
        else:
            info(
                "Session is not interactive (usually this happens during a CI run), so let's consider it as a YES"
            )
            return True

    def install(self):
        info(f"python-for-android can automatically install prerequisite: {self.name}")
        if self.ask_to_install():
            if sys.platform == "darwin":
                self.darwin_installer()
            elif sys.platform == "linux":
                self.linux_installer()
            else:
                raise Exception("Unsupported platform")
        else:
            info(
                f"Skipping installation of prerequisite {self.name} as per user request"
            )

    def show_helper(self):
        if sys.platform == "darwin":
            self.darwin_helper()
        elif sys.platform == "linux":
            self.linux_helper()
        else:
            raise Exception("Unsupported platform")

    def install_is_supported(self):
        if sys.platform == "darwin":
            return self.darwin_installer_is_supported
        elif sys.platform == "linux":
            return self.linux_installer_is_supported

    def linux_checker(self):
        raise Exception(f"Unsupported prerequisite check on linux for {self.name}")

    def darwin_checker(self):
        raise Exception(f"Unsupported prerequisite check on macOS for {self.name}")

    def linux_installer(self):
        raise Exception(f"Unsupported prerequisite installer on linux for {self.name}")

    def darwin_installer(self):
        raise Exception(f"Unsupported prerequisite installer on macOS for {self.name}")

    def darwin_helper(self):
        info(f"No helper available for prerequisite: {self.name} on macOS")

    def linux_helper(self):
        info(f"No helper available for prerequisite: {self.name} on linux")


class JDKPrerequisite(Prerequisite):
    name = "JDK"
    mandatory = True
    darwin_installer_is_supported = True
    min_supported_version = 11

    def darwin_checker(self):
        if "JAVA_HOME" in os.environ:
            info("Found JAVA_HOME environment variable, using it")
            jdk_path = os.environ["JAVA_HOME"]
        else:
            jdk_path = self._darwin_get_libexec_jdk_path(version=None)
        return self._darwin_jdk_is_supported(jdk_path)

    def _darwin_get_libexec_jdk_path(self, version=None):
        version_args = []
        if version is not None:
            version_args = ["-v", version]
        return (
            subprocess.run(
                ["/usr/libexec/java_home", *version_args],
                stdout=subprocess.PIPE,
            )
            .stdout.strip()
            .decode()
        )

    def _darwin_jdk_is_supported(self, jdk_path):
        if not jdk_path:
            return False

        javac_bin = os.path.join(jdk_path, "bin", "javac")
        if not os.path.exists(javac_bin):
            return False

        p = subprocess.Popen(
            [javac_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        _stdout_res, _stderr_res = p.communicate()

        if p.returncode != 0:
            error("Failed to run javac to check JDK version")
            return False

        if not _stdout_res:
            _stdout_res = _stderr_res

        res = _stdout_res.strip().decode()

        major_version = int(res.split(" ")[-1].split(".")[0])
        if major_version >= self.min_supported_version:
            info(f"Found a valid JDK at {jdk_path}")
            return True
        else:
            error(f"JDK {self.min_supported_version} or higher is required")
            return False

    def darwin_helper(self):
        info(
            "python-for-android requires a JDK 11 or higher to be installed on macOS,"
            "but seems like you don't have one installed."
        )
        info(
            "If you think that a valid JDK is already installed, please verify that "
            "you have a JDK 11 or higher installed and that `/usr/libexec/java_home` "
            "shows the correct path."
        )
        info(
            "If you have multiple JDK installations, please make sure that you have "
            "`JAVA_HOME` environment variable set to the correct JDK installation."
        )

    def darwin_installer(self):
        info(
            "Looking for a JDK 11 or higher installation which is not the default one ..."
        )
        jdk_path = self._darwin_get_libexec_jdk_path(version="11+")

        if not self._darwin_jdk_is_supported(jdk_path):
            info("We're unlucky, there's no JDK 11 or higher installation available")

            base_url = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.2%2B8/"
            if platform.machine() == "arm64":
                filename = "OpenJDK17U-jdk_aarch64_mac_hotspot_17.0.2_8.tar.gz"
            else:
                filename = "OpenJDK17U-jdk_x64_mac_hotspot_17.0.2_8.tar.gz"

            info(f"Downloading {filename} from {base_url}")
            subprocess.check_output(
                [
                    "curl",
                    "-L",
                    f"{base_url}{filename}",
                    "-o",
                    f"/tmp/{filename}",
                ]
            )

            user_library_java_path = os.path.expanduser(
                "~/Library/Java/JavaVirtualMachines"
            )
            info(f"Extracting {filename} to {user_library_java_path}")
            subprocess.check_output(
                [
                    "mkdir",
                    "-p",
                    user_library_java_path,
                ],
            )
            subprocess.check_output(
                ["tar", "xzf", f"/tmp/{filename}", "-C", user_library_java_path],
            )

            jdk_path = self._darwin_get_libexec_jdk_path(version="17.0.2+8")

        info(f"Setting JAVA_HOME to {jdk_path}")
        os.environ["JAVA_HOME"] = jdk_path


def check_and_install_default_prerequisites():
    DEFAULT_PREREQUISITES = dict(darwin=[JDKPrerequisite()], linux=[], all_platforms=[])

    required_prerequisites = (
        DEFAULT_PREREQUISITES["all_platforms"] + DEFAULT_PREREQUISITES[sys.platform]
    )

    prerequisites_not_met = []

    warning(
        "prerequisites.py is experimental and does not support all prerequisites yet."
    )
    warning("Please report any issues to the python-for-android issue tracker.")

    # Phase 1: Check if all prerequisites are met and add the ones
    # which are not to `prerequisites_not_met`
    for prerequisite in required_prerequisites:
        if not prerequisite.is_valid():
            prerequisites_not_met.append(prerequisite)

    # Phase 2: Setup/Install all prerequisites that are not met
    # (where possible), otherwise show an helper.
    for prerequisite in prerequisites_not_met:
        prerequisite.show_helper()
        if prerequisite.install_is_supported():
            prerequisite.install()


if __name__ == "__main__":
    check_and_install_default_prerequisites()
