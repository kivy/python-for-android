""" This module offers highlevel functions to get package metadata
    like the METADATA file, the name, or a list of dependencies.

    Usage examples:

       # Getting package name from pip reference:
       from pytonforandroid.pythonpackage import get_package_name
       print(get_package_name("pillow"))
       # Outputs: "Pillow" (note the spelling!)

       # Getting package dependencies:
       from pytonforandroid.pythonpackage import get_package_dependencies
       print(get_package_dependencies("pep517"))
       # Outputs: "['pytoml']"

       # Get package name from arbitrary package source:
       from pytonforandroid.pythonpackage import get_package_name
       print(get_package_name("/some/local/project/folder/"))
       # Outputs package name

    NOTE:

    Yes, this module doesn't fit well into python-for-android, but this
    functionality isn't available ANYWHERE ELSE, and upstream (pip, ...)
    currently has no interest in taking this over, so it has no other place
    to go.
    (Unless someone reading this puts it into yet another packaging lib)

    Reference discussion/upstream inclusion attempt:

    https://github.com/pypa/packaging-problems/issues/247

"""


from io import open  # needed for python 2
import os
from pep517.envbuild import BuildEnvironment
from pep517.wrappers import Pep517HookCaller
import pytoml
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import time
try:
    from urllib.parse import urlparse
    from urllib.parse import unquote as urlunquote
except ImportError:  # Python 2...
    from urlparse import urlparse
    from urlparse import unquote as urlunquote
import zipfile


def transform_dep_for_pip(dependency):
    if dependency.find("@") > 0:
        # WORKAROUND FOR UPSTREAM BUG:
        # https://github.com/pypa/pip/issues/6097
        # (Please REMOVE workaround once that is fixed & released upstream!)
        #
        # Basically, setup_requires() can contain a format pip won't install
        # from a requirements.txt (PEP 508 URLs).
        # To avoid this, translate to an #egg-name= reference:
        url = (dependency.partition("@")[2].strip() +
               "#egg-name=" +
               dependency.partition("@")[0].strip()
              )
        return url
    return dependency


def extract_metainfo_files_from_package(
        package,
        output_folder,
        debug=False
        ):
    """ Extracts metdata files from the given package to the given folder,
        which may be referenced in any way that is permitted in
        a requirements.txt file or install_requires=[] listing.

        Current supported metadata files that will be extracted:

        - pytoml.yml  (only if package wasn't obtained as wheel)
        - METADATA
    """

    if package is None:
        raise ValueError("package cannot be None")

    if not os.path.exists(output_folder) or os.path.isfile(output_folder):
        raise ValueError("output folder needs to be existing folder")

    # A temp folder for making a package copy in case it's a local folder,
    # because extracting metadata might modify files
    # (creating sdists/wheels...)
    temp_folder = tempfile.mkdtemp(prefix="pythonpackage-package-copy-")
    try:
        # Package is indeed a folder! Get a temp copy to work on:
        if is_filesystem_path(package):
            shutil.copytree(
                parse_as_folder_reference(package),
                os.path.join(temp_folder, "package")
            )
            package = os.path.join(temp_folder, "package")

        # Because PEP517 can be noisy and contextlib.redirect_* fails to
        # contain it, we will run the actual analysis in a separate process:
        try:
            subprocess.check_output([
                sys.executable,
                "-c",
                "import importlib\n"
                "import json\n"
                "import os\n"
                "import sys\n"
                "sys.path = [os.path.dirname(sys.argv[3])] + sys.path\n"
                "m = importlib.import_module(\n"
                "    os.path.basename(sys.argv[3]).partition('.')[0]\n"
                ")\n"
                "m._extract_metainfo_files_from_package_unsafe("
                "    sys.argv[1],"
                "    sys.argv[2],"
                ")",
                package, output_folder, os.path.abspath(__file__)],
                stderr=subprocess.STDOUT,  # make sure stderr is muted.
                cwd=os.path.join(os.path.dirname(__file__), "..")
            )
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8", "replace")
            if debug:
                print("Got error obtaining meta info.")
                print("Detail output:")
                print(output)
                print("End of Detail output.")
            raise ValueError(
                "failed to obtain meta info - "
                "is '{}' a valid package? "
                "Detailed output:\n{}".format(package, output)
                )
    finally:
        shutil.rmtree(temp_folder)


def _get_system_python_executable():
    """ Returns the path the system-wide python binary.
        (In case we're running in a virtualenv or venv)
    """
    # This function is required by get_package_as_folder() to work
    # inside a virtualenv, since venv creation will fail with
    # the virtualenv's local python binary.
    # (venv/virtualenv incompatibility)

    # Abort if not in virtualenv or venv:
    if not hasattr(sys, "real_prefix") and (
            not hasattr(sys, "base_prefix") or
            os.path.normpath(sys.base_prefix) ==
            os.path.normpath(sys.prefix)):
        return sys.executable

    # Extract prefix we need to look in:
    if hasattr(sys, "real_prefix"):
        search_prefix = sys.real_prefix  # virtualenv
    else:
        search_prefix = sys.base_prefix  # venv

    def python_binary_from_folder(path):
        def binary_is_usable(python_bin):
            try:
                filenotfounderror = FileNotFoundError
            except NameError:  # Python 2
                filenotfounderror = OSError
            try:
                subprocess.check_output([
                    os.path.join(path, python_bin), "--version"
                ], stderr=subprocess.STDOUT)
                return True
            except (subprocess.CalledProcessError, filenotfounderror):
                return False

        python_name = "python" + sys.version
        while (not binary_is_usable(python_name) and
               python_name.find(".") > 0):
            # Try less specific binary name:
            python_name = python_name.rpartition(".")[0]
        if binary_is_usable(python_name):
            return os.path.join(path, python_name)
        return None

    # Return from sys.real_prefix if present:
    result = python_binary_from_folder(search_prefix)
    if result is not None:
        return result

    # Check out all paths in $PATH:
    bad_candidates = []
    good_candidates = []
    ever_had_nonvenv_path = False
    for p in os.environ.get("PATH", "").split(":"):
        # Skip if not possibly the real system python:
        if not os.path.normpath(p).startswith(
                os.path.normpath(search_prefix)
                ):
            continue

        # First folders might be virtualenv/venv we want to avoid:
        if not ever_had_nonvenv_path:
            sep = os.path.sep
            if ("system32" not in p.lower() and "usr" not in p) or \
                    {"home", ".tox"}.intersection(set(p.split(sep))) or \
                    "users" in p.lower():
                # Doesn't look like bog-standard system path.
                if (p.endswith(os.path.sep + "bin") or
                        p.endswith(os.path.sep + "bin" + os.path.sep)):
                    # Also ends in "bin" -> likely virtualenv/venv.
                    # Add as unfavorable / end of candidates:
                    bad_candidates.append(p)
                    continue
            ever_had_nonvenv_path = True

        good_candidates.append(p)

    # See if we can now actually find the system python:
    for p in good_candidates + bad_candidates:
        result = python_binary_from_folder(p)
        if result is not None:
            return result

    raise RuntimeError("failed to locate system python in: " +
                       sys.real_prefix)


def get_package_as_folder(dependency):
    """ This function downloads the given package / dependency and extracts
        the raw contents into a folder.

        Afterwards, it returns a tuple with the type of distribution obtained,
        and the temporary folder it extracted to. It is the caller's
        responsibility to delete the returned temp folder after use.

        Examples of returned values:

        ("source", "/tmp/pythonpackage-venv-e84toiwjw")
        ("wheel", "/tmp/pythonpackage-venv-85u78uj")

        What the distribution type will be depends on what pip decides to
        download.
    """

    venv_parent = tempfile.mkdtemp(
        prefix="pythonpackage-venv-"
    )
    try:
        # Create a venv to install into:
        try:
            if int(sys.version.partition(".")[0]) < 3:
                # Python 2.x has no venv.
                subprocess.check_output([
                    sys.executable,  # no venv conflict possible,
                                     # -> no need to use system python
                    "-m", "virtualenv",
                    "--python=" + _get_system_python_executable(),
                    os.path.join(venv_parent, 'venv')
                ], cwd=venv_parent)
            else:
                # On modern Python 3, use venv.
                subprocess.check_output([
                    _get_system_python_executable(), "-m", "venv",
                    os.path.join(venv_parent, 'venv')
                ], cwd=venv_parent)
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8', 'replace')
            raise ValueError(
                'venv creation unexpectedly ' +
                'failed. error output: ' + str(output)
            )
        venv_path = os.path.join(venv_parent, "venv")

        # Update pip and wheel in venv for latest feature support:
        try:
            filenotfounderror = FileNotFoundError
        except NameError:  # Python 2.
            filenotfounderror = OSError
        try:
            subprocess.check_output([
                os.path.join(venv_path, "bin", "pip"),
                "install", "-U", "pip", "wheel",
            ])
        except filenotfounderror:
            raise RuntimeError(
                "venv appears to be missing pip. "
                "did we fail to use a proper system python??\n"
                "system python path detected: {}\n"
                "os.environ['PATH']: {}".format(
                    _get_system_python_executable(),
                    os.environ.get("PATH", "")
                )
            )

        # Create download subfolder:
        os.mkdir(os.path.join(venv_path, "download"))

        # Write a requirements.txt with our package and download:
        with open(os.path.join(venv_path, "requirements.txt"),
                  "w", encoding="utf-8"
                 ) as f:
            def to_unicode(s):  # Needed for Python 2.
                try:
                    return s.decode("utf-8")
                except AttributeError:
                    return s
            f.write(to_unicode(transform_dep_for_pip(dependency)))
        try:
            subprocess.check_output(
                [
                    os.path.join(venv_path, "bin", "pip"),
                    "download", "--no-deps", "-r", "../requirements.txt",
                    "-d", os.path.join(venv_path, "download")
                ],
                stderr=subprocess.STDOUT,
                cwd=os.path.join(venv_path, "download")
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("package download failed: " + str(e.output))

        if len(os.listdir(os.path.join(venv_path, "download"))) == 0:
            # No download. This can happen if the dependency has a condition
            # which prohibits install in our environment.
            # (the "package ; ... conditional ... " type of condition)
            return (None, None)

        # Get the result and make sure it's an extracted directory:
        result_folder_or_file = os.path.join(
            venv_path, "download",
            os.listdir(os.path.join(venv_path, "download"))[0]
        )
        dl_type = "source"
        if not os.path.isdir(result_folder_or_file):
            # Must be an archive.
            if result_folder_or_file.endswith((".zip", ".whl")):
                if result_folder_or_file.endswith(".whl"):
                    dl_type = "wheel"
                with zipfile.ZipFile(result_folder_or_file) as f:
                    f.extractall(os.path.join(venv_path,
                                              "download", "extracted"
                                             ))
                    result_folder_or_file = os.path.join(
                        venv_path, "download", "extracted"
                    )
            elif result_folder_or_file.find(".tar.") > 0:
                # Probably a tarball.
                with tarfile.open(result_folder_or_file) as f:
                    f.extractall(os.path.join(venv_path,
                                              "download", "extracted"
                                             ))
                    result_folder_or_file = os.path.join(
                        venv_path, "download", "extracted"
                    )
            else:
                raise RuntimeError(
                    "unknown archive or download " +
                    "type: " + str(result_folder_or_file)
                )

        # If the result is hidden away in an additional subfolder,
        # descend into it:
        while os.path.isdir(result_folder_or_file) and \
                len(os.listdir(result_folder_or_file)) == 1 and \
                os.path.isdir(os.path.join(
                    result_folder_or_file,
                    os.listdir(result_folder_or_file)[0]
                )):
            result_folder_or_file = os.path.join(
                result_folder_or_file,
                os.listdir(result_folder_or_file)[0]
            )

        # Copy result to new dedicated folder so we can throw away
        # our entire virtualenv nonsense after returning:
        result_path = tempfile.mkdtemp()
        shutil.rmtree(result_path)
        shutil.copytree(result_folder_or_file, result_path)
        return (dl_type, result_path)
    finally:
        shutil.rmtree(venv_parent)


def _extract_metainfo_files_from_package_unsafe(
        package,
        output_path
        ):
    # This is the unwrapped function that will
    # 1. make lots of stdout/stderr noise
    # 2. possibly modify files (if the package source is a local folder)
    # Use extract_metainfo_files_from_package_folder instead which avoids
    # these issues.

    clean_up_path = False
    path_type = "source"
    path = parse_as_folder_reference(package)
    if path is None:
        # This is not a path. Download it:
        (path_type, path) = get_package_as_folder(package)
        if path_type is None:
            # Download failed.
            raise ValueError(
                "cannot get info for this package, " +
                "pip says it has no downloads (conditional dependency?)"
            )
        clean_up_path = True

    try:
        build_requires = []
        metadata_path = None
        if path_type != "wheel":
            # We need to process this first to get the metadata.

            # Ensure pyproject.toml is available (pep517 expects it)
            if not os.path.exists(os.path.join(path, "pyproject.toml")):
                with open(os.path.join(path, "pyproject.toml"), "w") as f:
                    f.write(textwrap.dedent(u"""\
                    [build-system]
                    requires = ["setuptools", "wheel"]
                    build-backend = "setuptools.build_meta"
                    """))

            # Copy the pyproject.toml:
            shutil.copyfile(
                os.path.join(path, 'pyproject.toml'),
                os.path.join(output_path, 'pyproject.toml')
            )

            # Get build backend from pyproject.toml:
            with open(os.path.join(path, 'pyproject.toml')) as f:
                build_sys = pytoml.load(f)['build-system']
                backend = build_sys["build-backend"]

            # Get a virtualenv with build requirements and get all metadata:
            env = BuildEnvironment()
            metadata = None
            with env:
                hooks = Pep517HookCaller(path, backend)
                env.pip_install([transform_dep_for_pip(req) for req in build_requires])
                reqs = hooks.get_requires_for_build_wheel({})
                env.pip_install([transform_dep_for_pip(req) for req in reqs])
                try:
                    metadata = hooks.prepare_metadata_for_build_wheel(path)
                except Exception:  # sadly, pep517 has no good error here
                    pass
            if metadata is not None:
                metadata_path = os.path.join(
                    path, metadata, "METADATA"
                )
        else:
            # This is a wheel, so metadata should be in *.dist-info folder:
            metadata_path = os.path.join(
                path,
                [f for f in os.listdir(path) if f.endswith(".dist-info")][0],
                "METADATA"
            )

        # Copy the metadata file:
        shutil.copyfile(metadata_path, os.path.join(output_path, "METADATA"))
    finally:
        if clean_up_path:
            shutil.rmtree(path)


def is_filesystem_path(dep):
    """ Convenience function around parse_as_folder_reference() to
        check if a dependency refers to a folder path or something remote.

        Returns True if local, False if remote.
    """
    return (parse_as_folder_reference(dep) is not None)


def parse_as_folder_reference(dep):
    """ See if a dependency reference refers to a folder path.
        If it does, return the folder path (which parses and
        resolves file:// urls in the process).
        If it doesn't, return None.
    """
    # Special case: pep508 urls
    if dep.find("@") > 0 and (
            (dep.find("@") < dep.find("/") or "/" not in dep) and
            (dep.find("@") < dep.find(":") or ":" not in dep)
            ):
        # This should be a 'pkgname @ https://...' style path, or
        # 'pkname @ /local/file/path'.
        return parse_as_folder_reference(dep.partition("@")[2].lstrip())

    # Check if this is either not an url, or a file URL:
    if dep.startswith(("/", "file://")) or (
            dep.find("/") > 0 and
            dep.find("://") < 0):
        if dep.startswith("file://"):
            dep = urlunquote(urlparse(dep).path)
        return dep
    return None


def _extract_info_from_package(dependency,
                               extract_type=None,
                               debug=False,
                               include_build_requirements=False
                               ):
    """ Internal function to extract metainfo from a package.
        Currently supported info types:

        - name
        - dependencies  (a list of dependencies)
    """
    output_folder = tempfile.mkdtemp(prefix="pythonpackage-metafolder-")
    try:
        extract_metainfo_files_from_package(
            dependency, output_folder, debug=debug
        )

        with open(os.path.join(output_folder, "METADATA"),
                  "r", encoding="utf-8"
                 ) as f:
            # Get metadata and cut away description (is after 2 linebreaks)
            metadata_entries = f.read().partition("\n\n")[0].splitlines()

        if extract_type == "name":
            name = None
            for meta_entry in metadata_entries:
                if meta_entry.lower().startswith("name:"):
                    return meta_entry.partition(":")[2].strip()
            if name is None:
                raise ValueError("failed to obtain package name")
            return name
        elif extract_type == "dependencies":
            requirements = []
            if os.path.exists(os.path.join(output_folder,
                                           'pyproject.toml')
                              ) and include_build_requirements:
                with open(os.path.join(output_folder, 'pyproject.toml')) as f:
                    build_sys = pytoml.load(f)['build-system']
                    if "requires" in build_sys:
                        requirements += build_sys["requires"]

            # Add requirements from metadata:
            requirements += [
                entry.rpartition("Requires-Dist:")[2].strip()
                for entry in metadata_entries
                if entry.startswith("Requires-Dist")
            ]

            return list(set(requirements))  # remove duplicates
    finally:
        shutil.rmtree(output_folder)


package_name_cache = dict()


def get_package_name(dependency,
                     use_cache=True):
    def timestamp():
        try:
            return time.monotonic()
        except AttributeError:
            return time.time()  # Python 2.
    try:
        value = package_name_cache[dependency]
        if value[0] + 600.0 > timestamp() and use_cache:
            return value[1]
    except KeyError:
        pass
    result = _extract_info_from_package(dependency, extract_type="name")
    package_name_cache[dependency] = (timestamp(), result)
    return result


def get_package_dependencies(package,
                             recursive=False,
                             verbose=False,
                             include_build_requirements=False):
    """ Obtain the dependencies from a package. Please note this
        function is possibly SLOW, especially if you enable
        the recursive mode.
    """
    packages_processed = set()
    package_queue = [package]
    reqs = set()
    reqs_as_names = set()
    while len(package_queue) > 0:
        current_queue = package_queue
        package_queue = []
        for package_dep in current_queue:
            new_reqs = set()
            if verbose:
                print("get_package_dependencies: resolving dependecy "
                      "to package name: ".format(package_dep))
            package = get_package_name(package_dep)
            if package.lower() in packages_processed:
                continue
            if verbose:
                print("get_package_dependencies: "
                      "processing package: {}".format(package))
                print("get_package_dependencies: "
                      "Packages seen so far: {}".format(
                          packages_processed
                      ))
            packages_processed.add(package.lower())

            # Use our regular folder processing to examine:
            new_reqs = new_reqs.union(_extract_info_from_package(
                package_dep, extract_type="dependencies",
                debug=verbose,
                include_build_requirements=include_build_requirements,
            ))

            # Process new requirements:
            if verbose:
                print('get_package_dependencies: collected '
                      "deps of '{}': {}".format(
                          package_dep, str(new_reqs),
                      ))
            for new_req in new_reqs:
                try:
                    req_name = get_package_name(new_req)
                except ValueError as e:
                    if new_req.find(";") >= 0:
                        # Conditional dep where condition isn't met?
                        # --> ignore it
                        continue
                    if verbose:
                        print("get_package_dependencies: " +
                              "unexpected failure to get name " +
                              "of '" + str(new_req) + "': " +
                              str(e))
                    raise RuntimeError(
                        "failed to get " +
                        "name of dependency: " + str(e)
                    )
                if req_name.lower() in reqs_as_names:
                    continue
                if req_name.lower() not in packages_processed:
                    package_queue.append(new_req)
                reqs.add(new_req)
                reqs_as_names.add(req_name.lower())

            # Bail out here if we're not scanning recursively:
            if not recursive:
                package_queue[:] = []  # wipe queue
                break
    if verbose:
        print("get_package_dependencies: returning result: {}".format(reqs))
    return reqs


def get_dep_names_of_package(
        package,
        keep_version_pins=False,
        recursive=False,
        verbose=False,
        include_build_requirements=False
        ):
    """ Gets the dependencies from the package in the given folder,
        then attempts to deduce the actual package name resulting
        from each dependency line, stripping away everything else.
    """

    # First, obtain the dependencies:
    dependencies = get_package_dependencies(
        package, recursive=recursive, verbose=verbose,
        include_build_requirements=include_build_requirements,
    )
    if verbose:
        print("get_dep_names_of_package_folder: " +
              "processing dependency list to names: " +
              str(dependencies))

    # Transform dependencies to their stripped down names:
    # (they can still have version pins/restrictions, conditionals, ...)
    dependency_names = set()
    for dep in dependencies:
        # If we are supposed to keep exact version pins, extract first:
        pin_to_append = ""
        if keep_version_pins and "(==" in dep and dep.endswith(")"):
            # This is a dependency of the format: 'pkg (==1.0)'
            pin_to_append = "==" + dep.rpartition("==")[2][:-1]
        elif keep_version_pins and "==" in dep and not dep.endswith(")"):
            # This is a dependency of the format: 'pkg==1.0'
            pin_to_append = "==" + dep.rpartition("==")[2]
        # Now get true (and e.g. case-corrected) dependency name:
        dep_name = get_package_name(dep) + pin_to_append
        dependency_names.add(dep_name)
    return dependency_names
