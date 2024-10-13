from reedsolo import *
import regex as re
from scanf import scanf

# Class for GF(256) elements, overloads operations

class gf_elt:

    tables_initiated = False

    def __init__(self, val):
        val = int(val)
        assert val in range(256)
        self.val = val

        if not gf_elt.tables_initiated:

            gf_elt.tables_initiated = True

            init_tables()

    def __add__(self, term):
        return gf_elt(gf_add(self.val, term.val))
    
    def __sub__(self, term):
        return gf_elt(gf_sub(self.val, term.val))
    
    def __mul__(self, factor):
        return gf_elt(gf_mul(self.val, factor.val))

    def __truediv__(self, diviser):
        return gf_elt(gf_div(self.val, diviser.val))

    def __floordiv__(self, div):
        return self / div
    
    def __pow__(self, pow):
        return gf_elt(gf_pow(self.val, pow))
    
    def __eq__(self, other):
        return self.val == other.val
    
    def __ne__(self, other):
        return self.val != other.val
    
    def __str__(self):
        return str(self.val)
    
def main():

    while True:

        x1, op, x2 = scanf("%d%s%d", collapseWhitespace=True)

        match (gf_elt(x1), op, gf_elt(x2)):
            case x1, "+", x2:
                print(x1 + x2)
            case x1, "*", x2:
                print(x1 * x2)
            case x1, "-", x2:
                print(x1 - x2)
            case x1, "/", x2:
                print(x1 / x2)
            case x1, "**", x2:
                print(x1 ** (x2.val))

if __name__ == "__main__":
    gf_elt(2)
    print(gf_pow(2, 21))
    main()

n = 10
k = 5

[[print(gf_elt(2) ** ( (7 - m) % 8 + j * (n + k - (m // 8) - 1))) for m in range(16)] for j in range(k)]

