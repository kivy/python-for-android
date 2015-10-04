#!/usr/bin/env sh

# This file is just a shim to report an error messaage if some tool
# tries to run the old python-for-android.

# An alternative would be to implement argument handling and pass
# things to the new toolchain so that it works the same as before, but
# that would be harder.


cat <<EOF
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

PYTHON-FOR-ANDROID ERROR! SEE BELOW FOR SOLUTION:

You are trying to run an old version of python-for-android via
distribute.sh. However, python-for-android has been rewritten and no
longer supports the distribute.sh interface.

If you are using buildozer, you should:
- upgrade buildozer to the latest version (at least 0.30)
- delete the .buildozer folder in your app directory (the same directory that has your buildozer.spec)
- run buildozer again as normal

If you are not using buildozer, see
https://github.com/kivy/python-for-android/blob/master/README.md for
instructions on using the new python-for-android
toolchain. Alternatively, you can get the old toolchain from the
'old_toolchain' branch at
https://github.com/kivy/python-for-android/tree/old_toolchain .

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
EOF

exit 1
