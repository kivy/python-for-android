from ctypes import CDLL, CFUNCTYPE, POINTER, byref, c_char_p, c_int, c_void_p, cast
import ctypes.util
import glob
import os
import sys

_sdl_lib = None
_sdl_get_proc_c = None
_android_jvm_registered = False


def _sdl_search_order():
    if "kivy.core.window.window_sdl3" in sys.modules:
        return ("SDL3", "SDL2")
    if "kivy.core.window.window_sdl2" in sys.modules:
        return ("SDL2", "SDL3")
    return ("SDL3", "SDL2")


def _find_sdl():
    order = _sdl_search_order()
    patterns = {
        "SDL3": ("libSDL3-*.so*",),
        "SDL2": ("libSDL2-*.so*",),
    }

    # Search site-packages (Kivy.libs / kivy.libs) first
    for p in sys.path:
        for libs_dir in ("Kivy.libs", "kivy.libs"):
            d = os.path.join(p, libs_dir)
            if os.path.isdir(d):
                for name in order:
                    for pat in patterns[name]:
                        for f in glob.glob(os.path.join(d, pat)):
                            bn = os.path.basename(f)
                            if "ttf" not in bn and "mix" not in bn and "image" not in bn:
                                return f

    # Fall back to system libraries
    for name in order:
        found = ctypes.util.find_library(name)
        if found:
            return found
    for name in order:
        soname = f"lib{name}.so"
        try:
            CDLL(soname)
            return soname
        except OSError:
            continue
    return None


def _get_sdl_lib():
    global _sdl_lib
    if _sdl_lib is None:
        sdl_path = _find_sdl()
        if not sdl_path:
            return None
        _sdl_lib = CDLL(sdl_path)
    return _sdl_lib


def _get_android_jni_env_fn(sdl_lib):
    # SDL3 renamed SDL_AndroidGetJNIEnv -> SDL_GetAndroidJNIEnv
    for sym in ("SDL_GetAndroidJNIEnv", "SDL_AndroidGetJNIEnv"):
        fn = getattr(sdl_lib, sym, None)
        if fn is not None:
            return fn
    raise AttributeError(
        "Neither SDL_GetAndroidJNIEnv nor SDL_AndroidGetJNIEnv found in SDL library"
    )


def ensure_android_java_vm():
    global _android_jvm_registered
    if _android_jvm_registered or sys.platform != "android":
        return
    _android_jvm_registered = True
    sdl_lib = _get_sdl_lib()
    if sdl_lib is None:
        return
    get_jni_env = _get_android_jni_env_fn(sdl_lib)
    get_jni_env.restype = c_void_p
    jni_env = get_jni_env()
    if not jni_env:
        return
    fn_table = cast(jni_env, POINTER(POINTER(c_void_p))).contents
    get_java_vm = CFUNCTYPE(c_int, c_void_p, POINTER(c_void_p))(fn_table[219])
    java_vm = c_void_p()
    if get_java_vm(jni_env, byref(java_vm)) == 0 and java_vm.value:
        try:
            libavcodec = CDLL("libavcodec.so")
        except OSError:
            return
        libavcodec.av_jni_set_java_vm.argtypes = [c_void_p, c_void_p]
        libavcodec.av_jni_set_java_vm.restype = c_int
        libavcodec.av_jni_set_java_vm(java_vm, None)


def sdl_opengl_init_params():
    global _sdl_get_proc_c
    if _sdl_get_proc_c is None:
        sdl_lib = _get_sdl_lib()
        if sdl_lib is None:
            raise OSError("Cannot find SDL2/SDL3 shared library for OpenGL proc lookup")
        sdl_lib.SDL_GL_GetProcAddress.argtypes = [c_char_p]
        sdl_lib.SDL_GL_GetProcAddress.restype = c_void_p
        glproc_t = CFUNCTYPE(c_void_p, c_void_p, c_char_p)
        _sdl_get_proc_c = glproc_t(
            lambda _ctx, name: sdl_lib.SDL_GL_GetProcAddress(name)
        )
    return {"get_proc_address": _sdl_get_proc_c}
