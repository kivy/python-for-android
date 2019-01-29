from pythonforandroid.toolchain import Recipe

# if android app crashes on start with "ImportError: No module named websocket"
#
#     copy the 'websocket' directory into your app directory to force inclusion.
#
# see my example at https://github.com/debauchery1st/example_kivy_websocket-recipe
#
# If you see errors relating to 'SSL not available' ensure you have the package backports.ssl-match-hostname
# in the buildozer requirements, since Kivy targets python 2.7.x
#
# You may also need sslopt={"cert_reqs": ssl.CERT_NONE} as a parameter to ws.run_forever() if you get an error relating to
# host verification


class WebSocketClient(Recipe):

    url = 'https://github.com/websocket-client/websocket-client/archive/v{version}.tar.gz'

    version = '0.40.0'

    # patches = ['websocket.patch']  # Paths relative to the recipe dir

    depends = ['android', 'pyjnius', 'cryptography', 'pyasn1', 'pyopenssl']


recipe = WebSocketClient()
