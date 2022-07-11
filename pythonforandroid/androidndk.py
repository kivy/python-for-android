import sys
import os


class AndroidNDK:
    """
    This class is used to get the current NDK information.
    """

    ndk_dir = ""

    def __init__(self, ndk_dir):
        self.ndk_dir = ndk_dir

    @property
    def host_tag(self):
        """
        Returns the host tag for the current system.
        Note: The host tag is ``darwin-x86_64`` even on Apple Silicon macs.
        """
        return f"{sys.platform}-x86_64"

    @property
    def llvm_prebuilt_dir(self):
        return os.path.join(
            self.ndk_dir, "toolchains", "llvm", "prebuilt", self.host_tag
        )

    @property
    def llvm_bin_dir(self):
        return os.path.join(self.llvm_prebuilt_dir, "bin")

    @property
    def clang(self):
        return os.path.join(self.llvm_bin_dir, "clang")

    @property
    def clang_cxx(self):
        return os.path.join(self.llvm_bin_dir, "clang++")

    @property
    def llvm_binutils_prefix(self):
        return os.path.join(self.llvm_bin_dir, "llvm-")

    @property
    def llvm_ar(self):
        return f"{self.llvm_binutils_prefix}ar"

    @property
    def llvm_ranlib(self):
        return f"{self.llvm_binutils_prefix}ranlib"

    @property
    def llvm_objcopy(self):
        return f"{self.llvm_binutils_prefix}objcopy"

    @property
    def llvm_objdump(self):
        return f"{self.llvm_binutils_prefix}objdump"

    @property
    def llvm_readelf(self):
        return f"{self.llvm_binutils_prefix}readelf"

    @property
    def llvm_strip(self):
        return f"{self.llvm_binutils_prefix}strip"

    @property
    def sysroot(self):
        return os.path.join(self.llvm_prebuilt_dir, "sysroot")

    @property
    def sysroot_include_dir(self):
        return os.path.join(self.sysroot, "usr", "include")

    @property
    def sysroot_lib_dir(self):
        return os.path.join(self.sysroot, "usr", "lib")

    @property
    def libcxx_include_dir(self):
        return os.path.join(self.sysroot_include_dir, "c++", "v1")
