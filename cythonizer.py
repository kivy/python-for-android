import os, sys

class cythonizer():
    def __init__(self,
                 android_ndk        = os.environ["ANDROIDNDK"],
                 android_api        = os.environ["ANDROIDAPI"],
                 python_for_android = os.path.join(os.path.split(os.path.realpath(__file__))[0])
                 ):
        self.android_ndk = android_ndk
        self.android_api = android_api
        self.py_for_a    = python_for_android
        
        for path in [self.android_ndk, self.py_for_a]:
            if not os.path.isdir(path):
                print "!! Haven't found path:", repr(path)
                sys.exit()
        
        self.gcc     = "%s/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin/arm-linux-androideabi-gcc"  %(self.android_ndk)
        self.sysroot = "%s/platforms/android-%s/arch-arm"                                                            %(self.android_ndk, self.android_api)
        self.a_incl  = "-I%s/platforms/android-%s/arch-arm/usr/include"                                                %(self.android_ndk, self.android_api)
        self.p_incl  = "-I%s/build/python-install/include/python2.7"                                                   %(self.py_for_a)
        self.libs    = "-L%s/build/libs"                                                                             %(self.py_for_a)
        self.p_libs  = "-L%s/build/python-install/lib"                                                               %(self.py_for_a) 
        self.a_libs  = "-L%s/platforms/android-%s/arch-arm/usr/lib"                                                  %(self.android_ndk, self.android_api)
        
    def make_o(self, c_file, o_file):
        command = """%s -mandroid -fomit-frame-pointer -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC --sysroot %s  %s %s -c database.c -o database.o""" %(self.gcc, 
                           self.sysroot, 
                           self.a_incl, 
                           self.p_incl)
        print command
    
    def make_so(self, o_file, so_file= None):
        if so_file == None:
            so_file = os.path.splitext(os.path.realpath(o_file))[0]+".so"
        command = """%s -shared -O3 -mandroid -fomit-frame-pointer --sysroot %s -lm -lGLESv2 -lpython2.7 %s %s %s %s -o %s """ %(self.gcc,
                                                                                                                                 self.sysroot,
                                                                                                                                 self.libs,
                                                                                                                                 self.p_libs,
                                                                                                                                 self.a_libs,
                                                                                                                                 o_file,
                                                                                                                                 so_file)
        print command
    def make(self, py_pyx):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') or file.endswith('.pyx'):
                    print file
        self.make_o(py_pyx)
        self.make_so(py_pyx)
        
if __name__ == "__main__":
    c = cythonizer()
    c.make("test.py")