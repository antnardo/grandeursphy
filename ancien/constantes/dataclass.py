import decimal

class Decimal(decimal.Decimal):
    def test(self):
        print(1)

    def __add__(self, x):
        try:
            return super().__add__(x)
        except TypeError:
            print('[WARNING] Decimal class lost')
            return float(self)+x

    def __radd__(self, x):
        return self + x

    def __mul__(self, x):
        try:
            return super().__mul__(x)
        except TypeError:
            print('[WARNING] Decimal class lost')
            return float(self)*x

    def __rmul__(self, x):
        return self * x
