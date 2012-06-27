# Android-specific python services.

cdef extern int SDL_ANDROID_CheckPause()
cdef extern void SDL_ANDROID_WaitForResume()
cdef extern void SDL_ANDROID_MapKey(int scancode, int keysym)

def check_pause():
    return SDL_ANDROID_CheckPause()

def wait_for_resume():
    android_accelerometer_enable(False)
    SDL_ANDROID_WaitForResume()
    android_accelerometer_enable(accelerometer_enabled)

def map_key(scancode, keysym):
    SDL_ANDROID_MapKey(scancode, keysym)

# Android keycodes.
KEYCODE_UNKNOWN         = 0
KEYCODE_SOFT_LEFT       = 1
KEYCODE_SOFT_RIGHT      = 2
KEYCODE_HOME            = 3
KEYCODE_BACK            = 4
KEYCODE_CALL            = 5
KEYCODE_ENDCALL         = 6
KEYCODE_0               = 7
KEYCODE_1               = 8
KEYCODE_2               = 9
KEYCODE_3               = 10
KEYCODE_4               = 11
KEYCODE_5               = 12
KEYCODE_6               = 13
KEYCODE_7               = 14
KEYCODE_8               = 15
KEYCODE_9               = 16
KEYCODE_STAR            = 17
KEYCODE_POUND           = 18
KEYCODE_DPAD_UP         = 19
KEYCODE_DPAD_DOWN       = 20
KEYCODE_DPAD_LEFT       = 21
KEYCODE_DPAD_RIGHT      = 22
KEYCODE_DPAD_CENTER     = 23
KEYCODE_VOLUME_UP       = 24
KEYCODE_VOLUME_DOWN     = 25
KEYCODE_POWER           = 26
KEYCODE_CAMERA          = 27
KEYCODE_CLEAR           = 28
KEYCODE_A               = 29
KEYCODE_B               = 30
KEYCODE_C               = 31
KEYCODE_D               = 32
KEYCODE_E               = 33
KEYCODE_F               = 34
KEYCODE_G               = 35
KEYCODE_H               = 36
KEYCODE_I               = 37
KEYCODE_J               = 38
KEYCODE_K               = 39
KEYCODE_L               = 40
KEYCODE_M               = 41
KEYCODE_N               = 42
KEYCODE_O               = 43
KEYCODE_P               = 44
KEYCODE_Q               = 45
KEYCODE_R               = 46
KEYCODE_S               = 47
KEYCODE_T               = 48
KEYCODE_U               = 49
KEYCODE_V               = 50
KEYCODE_W               = 51
KEYCODE_X               = 52
KEYCODE_Y               = 53
KEYCODE_Z               = 54
KEYCODE_COMMA           = 55
KEYCODE_PERIOD          = 56
KEYCODE_ALT_LEFT        = 57
KEYCODE_ALT_RIGHT       = 58
KEYCODE_SHIFT_LEFT      = 59
KEYCODE_SHIFT_RIGHT     = 60
KEYCODE_TAB             = 61
KEYCODE_SPACE           = 62
KEYCODE_SYM             = 63
KEYCODE_EXPLORER        = 64
KEYCODE_ENVELOPE        = 65
KEYCODE_ENTER           = 66
KEYCODE_DEL             = 67
KEYCODE_GRAVE           = 68
KEYCODE_MINUS           = 69
KEYCODE_EQUALS          = 70
KEYCODE_LEFT_BRACKET    = 71
KEYCODE_RIGHT_BRACKET   = 72
KEYCODE_BACKSLASH       = 73
KEYCODE_SEMICOLON       = 74
KEYCODE_APOSTROPHE      = 75
KEYCODE_SLASH           = 76
KEYCODE_AT              = 77
KEYCODE_NUM             = 78
KEYCODE_HEADSETHOOK     = 79
KEYCODE_FOCUS           = 80
KEYCODE_PLUS            = 81
KEYCODE_MENU            = 82
KEYCODE_NOTIFICATION    = 83
KEYCODE_SEARCH          = 84
KEYCODE_MEDIA_PLAY_PAUSE= 85
KEYCODE_MEDIA_STOP      = 86
KEYCODE_MEDIA_NEXT      = 87
KEYCODE_MEDIA_PREVIOUS  = 88
KEYCODE_MEDIA_REWIND    = 89
KEYCODE_MEDIA_FAST_FORWARD = 90
KEYCODE_MUTE            = 91

# Activate input - required to receive input events.
cdef extern void android_activate_input()

def init():
    android_activate_input()

# Vibration support.
cdef extern void android_vibrate(double)

def vibrate(s):
    android_vibrate(s)

# Accelerometer support.
cdef extern void android_accelerometer_enable(int)
cdef extern void android_accelerometer_reading(float *)

accelerometer_enabled = False

def accelerometer_enable(p):
    global accelerometer_enabled

    android_accelerometer_enable(p)

    accelerometer_enabled = p

def accelerometer_reading():
    cdef float rv[3]
    android_accelerometer_reading(rv)

    return (rv[0], rv[1], rv[2])

# Wifi reading support
cdef extern void android_wifi_scanner_enable()
cdef extern char * android_wifi_scan()

def wifi_scanner_enable():
    android_wifi_scanner_enable()

def wifi_scan():
    cdef char * reading
    reading = android_wifi_scan()

    reading_list = []

    for line in filter(lambda l: l, reading.split('\n')):
        [ssid, mac, level] = line.split('\t')
        reading_list.append((ssid.strip(), mac.upper().strip(), int(level)))

    return reading_list

# DisplayMetrics information.
cdef extern int android_get_dpi()

def get_dpi():
    return android_get_dpi()


# Soft keyboard.
cdef extern void android_show_keyboard()
cdef extern void android_hide_keyboard()

def show_keyboard():
    android_show_keyboard()

def hide_keyboard():
    android_hide_keyboard()

# Build info.
cdef extern char* BUILD_MANUFACTURER
cdef extern char* BUILD_MODEL
cdef extern char* BUILD_PRODUCT
cdef extern char* BUILD_VERSION_RELEASE

cdef extern void android_get_buildinfo()

class BuildInfo:
    MANUFACTURER = None
    MODEL = None
    PRODUCT = None
    VERSION_RELEASE = None

def get_buildinfo():
    android_get_buildinfo()
    binfo = BuildInfo()
    binfo.MANUFACTURER = BUILD_MANUFACTURER
    binfo.MODEL = BUILD_MODEL
    binfo.PRODUCT = BUILD_PRODUCT
    binfo.VERSION_RELEASE = BUILD_VERSION_RELEASE
    return binfo

# Action send
cdef extern void android_action_send(char*, char*, char*, char*, char*)
def action_send(mimetype, filename=None, subject=None, text=None,
        chooser_title=None):
    cdef char *j_mimetype = <bytes>mimetype
    cdef char *j_filename = NULL
    cdef char *j_subject = NULL
    cdef char *j_text = NULL
    cdef char *j_chooser_title = NULL
    if filename is not None:
        j_filename = <bytes>filename
    if subject is not None:
        j_subject = <bytes>subject
    if text is not None:
        j_text = <bytes>text
    if chooser_title is not None:
        j_chooser_title = <bytes>chooser_title
    android_action_send(j_mimetype, j_filename, j_subject, j_text,
            j_chooser_title)

cdef extern int android_checkstop()
cdef extern void android_ackstop()

def check_stop():
    return android_checkstop()

def ack_stop():
    android_ackstop()

# -------------------------------------------------------------------
# URL Opening.
cdef extern void android_open_url(char *url)
def open_url(url):
    android_open_url(url)

# Web browser support.
class AndroidBrowser(object):
    def open(self, url, new=0, autoraise=True):
        open_url(url)
    def open_new(self, url):
        open_url(url)
    def open_new_tab(self, url):
        open_url(url)

import webbrowser
webbrowser.register('android', AndroidBrowser, None, -1)


