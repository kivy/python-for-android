'''
Runnable
========

'''

from jnius import PythonJavaClass, java_method, autoclass
from android.config import JAVA_NAMESPACE

# reference to the activity
_PythonActivity = autoclass(JAVA_NAMESPACE + '.PythonActivity')


class Runnable(PythonJavaClass):
    '''Wrapper around Java Runnable class. This class can be used to schedule a
    call of a Python function into the PythonActivity thread.
    '''

    __javainterfaces__ = ['java/lang/Runnable']
    __runnables__ = []

    def __init__(self, func):
        super(Runnable, self).__init__()
        self.func = func

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        Runnable.__runnables__.append(self)
        _PythonActivity.mActivity.runOnUiThread(self)

    @java_method('()V')
    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except:  # noqa E722
            import traceback
            traceback.print_exc()

        Runnable.__runnables__.remove(self)


def run_on_ui_thread(f):
    '''Decorator to create automatically a :class:`Runnable` object with the
    function. The function will be delayed and call into the Activity thread.
    '''
    def f2(*args, **kwargs):
        Runnable(f)(*args, **kwargs)
    return f2
