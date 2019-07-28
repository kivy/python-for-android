# Android-specific python services.

include "config.pxi"

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
cdef extern void android_show_keyboard(int)
cdef extern void android_hide_keyboard()


from jnius import autoclass, PythonJavaClass, java_method, cast

# API versions
api_version = autoclass('android.os.Build$VERSION').SDK_INT
version_codes = autoclass('android.os.Build$VERSION_CODES')


python_act = autoclass(JAVA_NAMESPACE + u'.PythonActivity')
Rect = autoclass(u'android.graphics.Rect')
mActivity = python_act.mActivity
if mActivity:
    # SDL2 now does not need the listener so there is
    # no point adding a processor intensive layout listenere here.
    height = 0
    def get_keyboard_height():
        rctx = Rect()
        mActivity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rctx)
        # NOTE top should always be zero
        rctx.top = 0
        height = mActivity.getWindowManager().getDefaultDisplay().getHeight() - (rctx.bottom - rctx.top)
        return height
else:
    def get_keyboard_height():
        return 0

# Flags for input_type, for requesting a particular type of keyboard
#android FLAGS
TYPE_CLASS_DATETIME = 4
TYPE_CLASS_NUMBER = 2
TYPE_NUMBER_VARIATION_NORMAL = 0
TYPE_NUMBER_VARIATION_PASSWORD = 16
TYPE_CLASS_TEXT = 1
TYPE_TEXT_FLAG_AUTO_COMPLETE = 65536
TYPE_TEXT_FLAG_AUTO_CORRECT = 32768
TYPE_TEXT_FLAG_NO_SUGGESTIONS = 524288
TYPE_TEXT_VARIATION_EMAIL_ADDRESS = 32
TYPE_TEXT_VARIATION_NORMAL = 0
TYPE_TEXT_VARIATION_PASSWORD = 128
TYPE_TEXT_VARIATION_POSTAL_ADDRESS = 112
TYPE_TEXT_VARIATION_URI = 16
TYPE_CLASS_PHONE = 3

IF BOOTSTRAP == 'sdl2':
    def remove_presplash():
        # Remove android presplash in SDL2 bootstrap.
        mActivity.removeLoadingScreen()

def show_keyboard(target, input_type):
    if input_type == 'text':
        _input_type = TYPE_CLASS_TEXT
    elif input_type == 'number':
        _input_type = TYPE_CLASS_NUMBER
    elif input_type == 'url':
        _input_type = \
            TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_URI
    elif input_type == 'mail':
        _input_type = \
            TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_EMAIL_ADDRESS
    elif input_type == 'datetime':
        _input_type = TYPE_CLASS_DATETIME
    elif input_type == 'tel':
        _input_type = TYPE_CLASS_PHONE
    elif input_type == 'address':
        _input_type = TYPE_TEXT_VARIATION_POSTAL_ADDRESS

    if hasattr(target, 'password') and target.password:
        if _input_type == TYPE_CLASS_TEXT:
            _input_type |= TYPE_TEXT_VARIATION_PASSWORD
        elif _input_type == TYPE_CLASS_NUMBER:
            _input_type |= TYPE_NUMBER_VARIATION_PASSWORD

    if hasattr(target, 'keyboard_suggestions') and not target.keyboard_suggestions:
        if _input_type == TYPE_CLASS_TEXT:
            _input_type = TYPE_CLASS_TEXT | \
                TYPE_TEXT_FLAG_NO_SUGGESTIONS

    android_show_keyboard(_input_type)

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

# -------------------------------------------------------------------
# URL Opening.
def open_url(url):
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    browserIntent = Intent()
    browserIntent.setAction(Intent.ACTION_VIEW)
    browserIntent.setData(Uri.parse(url))
    currentActivity = cast('android.app.Activity', mActivity)
    currentActivity.startActivity(browserIntent)
    return True

# Web browser support.
class AndroidBrowser(object):
    def open(self, url, new=0, autoraise=True):
        return open_url(url)
    def open_new(self, url):
        return open_url(url)
    def open_new_tab(self, url):
        return open_url(url)
    
import webbrowser
webbrowser.register('android', AndroidBrowser)


def start_service(title="Background Service",
                  description="", arg="",
                  as_foreground=True):
    # Legacy None value support (for old function signature style):
    if title is None:
        title = "Background Service"
    if description is None:
        description = ""
    if arg is None:
        arg = ""

    # Start service:
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    if as_foreground:
        mActivity.start_service(
            title, description, arg
        )
    else:
        mActivity.start_service_not_as_foreground(
            title, description, arg
        )


cdef extern void android_stop_service()
def stop_service():
    android_stop_service()

class AndroidService(object):
    '''Android service class.
    Run ``service/main.py`` from application directory as a service.

    :Parameters:
        `title`: str, default to 'Python service'
            Notification title.

        `description`: str, default to 'Kivy Python service started'
            Notification text.
    '''

    def __init__(self, title='Python service',
                 description='Kivy Python service started'):
        self.title = title
        self.description = description

    def start(self, arg=''):
        '''Start the service.

        :Parameters:
            `arg`: str, default to ''
                Argument to pass to a service,
                through environment variable ``PYTHON_SERVICE_ARGUMENT``.
        '''
        start_service(self.title, self.description, arg)

    def stop(self):
        '''Stop the service.
        '''
        stop_service()


