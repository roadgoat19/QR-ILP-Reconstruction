import sys
from qrcodegen import *

# Use this package: https://github.com/nayuki/QR-Code-generator/tree/master/python
def generate_QR(message, error_correction, masking, size):
    erclvl = None
    mask = -1
    N = 29

    match error_correction:
        case "low":
            erclvl = QrCode.Ecc.LOW
        case "med":
            erclvl = QrCode.Ecc.MEDIUM
        case "quart":
            erclvl = QrCode.Ecc.QUARTILE
        case "high":
            erclvl = QrCode.Ecc.HIGH
        case None:
            erclvl = None
        case _:
            raise Exception("Unknown error correction level: %s" % error_correction)
        
    match masking:
        case None | "-1":
            mask = -1
        case x:
            mask = int(x)

    match size:
        case "21":
            N = 21
        case _:
            N = 29

    segs = QrSegment.make_segments(message)
    
    # if erclvl is not None:
    #     return QrCode.encode_segments(segs = segs, ecl = erclvl, minversion = version(N), maxversion = version(N), mask = mask)
    # else:
    #     return QrCode.encode_segments(segs = segs, minversion = version(N), maxversion = version(N), mask = mask)
    return QrCode.encode_segments(segs = segs, ecl = erclvl, minversion = version(N), maxversion = version(N), mask = mask)

# From the qrcodegen library: size is between 21 and 177 (inclusive). This is equal to version * 4 + 17.
def version(size):
    return (size - 17) // 4


def handle_flags(argv, dic):
    match argv:
        case []:
            return dic
        case ["-e" | "-m" | "-s" | "-f" as flag, value, *rst]:
            if flag in dic:
                raise Exception(print("Flag given twice: %s" % flag))
            else:
                dic.setdefault(flag, value)
                return handle_flags(rst, dic)
        case [flag, *_]:
            raise Exception("arguments formatted improperly")

def file_output(code, name):

    size = code.get_size()

    arr = [[1 if code.get_module(i, j) else 0 for i in range(size)] for j in range(size)] # initialize 2D bit array representing the QR code: 0 for light, 1 for dark

    file = open("codes/%s" % name, "w")

    file.write("%d\n" % size) # I don't know if its worth putting size in the file


    for i in range(size):
        for j in range(size):
            file.write("%d" % arr[i][j])
        #file.write("\n")

#    def helper(row):
#        map(lambda bit: file.write("%d" % bit), row)
#        file.write("\n")

#    map(helper, arr)


def main():

    argc = len(sys.argv)

    match sys.argv:
        case [_, message, *rest]:
            options = handle_flags(rest, {})
            code = generate_QR(message = message, error_correction = options.get("-e"), masking = options.get("-m"), size = options.get("-s"))

            file_output(code, options.get("-f"))

            # for testing:
            print(str(options))

        case _:
            raise Exception("Requires message")

if __name__ == "__main__":
    main()



# file = open("test.svg", "w")
# file.write(svg)