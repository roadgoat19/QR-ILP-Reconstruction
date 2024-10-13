import pyqrcode
# Create a QR code
#qr = pyqrcode.create('Hello, World!', error='L', version=1)
qr = pyqrcode.create('Hello, World!', error='L', version=2)
#qr.png('hello_world.png', scale=1)
qr.png('codes/test.png', scale=1)
