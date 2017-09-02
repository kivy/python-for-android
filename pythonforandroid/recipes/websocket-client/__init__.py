from pythonforandroid.toolchain import Recipe

# if android app crashes on start with "ImportError: No module named websocket"
#
#     copy the 'websocket' directory into your app directory to force inclusion.
#
# see my example at https://github.com/debauchery1st/example_kivy_websocket-recipe


class WebSocketClient(Recipe):

    url = 'https://github.com/debauchery1st/websocket-client/raw/master/websocket_client-0.40.0.tar.gz'

    version = '0.40.0'
    # md5sum = 'f1cf4cc7869ef97a98e5f4be25c30986'

    # patches = ['websocket.patch']  # Paths relative to the recipe dir

    depends = ['kivy', 'python2', 'android', 'pyjnius',
               'cryptography', 'pyasn1', 'pyopenssl']

recipe = WebSocketClient()
