import pyqrcode

URL = "http://www.discoveranywheremobile.com/"
URL = "http://m.visitpalmsprings.com/listings/x-1fe89fc957e563c7/x-08cdb36014211c43/l-22c2cdd72d95ff48/"

qr_image = pyqrcode.MakeQRImage(URL, rounding = 5, fg = "black", bg = "burlywood", br = False)
qr_image.show()
