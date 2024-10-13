
import cv2

def png_reader(file):
    image = cv2.imread(file)

    detector = cv2.QRCodeDetector()

    match detector.detectAndDecode(image):
        case _, None, _:
            raise ValueError("No QR Code detected")
        case data, _, _:
            return data


def main():

    # Read the image
    image = cv2.imread('hello_world.png')

    # Initialize the QRCode detector
    detector = cv2.QRCodeDetector()

    # Detect and decode the QR code
    data, vertices_array, binary_qr_code = detector.detectAndDecode(image)

    if vertices_array is not None:
        print("QR Code data:", data)
    else:
        print("No QR Code detected.")


if __name__ == "__main__":
    main()