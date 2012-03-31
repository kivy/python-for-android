from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or "download_url"
# keywords (prior to python 2.3.0).
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
if not hasattr(DistributionMetadata, 'download_url'):
    DistributionMetadata.download_url = None
    
setup(
    name = 'pyqrcode',
    version = '0.1',
    description = 'Generate QR Codes',
    long_description = """\
Generate QR Codes
""",
    author='David Janes',
    author_email = 'support@discoveranywheremobile.com',
    url = 'http://code.davidjanes.com/',
    download_url = 'http://code.google.com/p/pyqrcode/source/checkout',
    license = "MIT",
    platforms = ['POSIX', 'Windows'],
    keywords = ['qrcodes',],
    classifiers = [
        ],
    py_modules = ['pyqrcode',]
    )
