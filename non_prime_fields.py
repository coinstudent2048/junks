# Construction of Non-prime fields
# Python 3
#
# Unoptimized and no error-checking. Coded for clarity instead.

# Field of prime order l. No prime checking of l
class PrimeField:
    def __init__(self, x, l):
        if isinstance(x, int) and isinstance(l, int) and l > 0:
            self.x = x % l
            self.l = l
        else:
            raise TypeError

    # Multiplicative inversion, with an option to let 1/0 = 0 if you're into that
    def invert(self, allow_zero=False):
        if self.x == 0:
            if allow_zero:
                return PrimeField(0, self.l)
            else:
                raise ZeroDivisionError
        return PrimeField(pow(self.x, self.l - 2, self.l), self.l)

    # Addition
    def __add__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return PrimeField(self.x + y.x, self.l)
        return NotImplemented

    # Subtraction
    def __sub__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return PrimeField(self.x - y.x, self.l)
        return NotImplemented

    # Multiplication (possibly by an integer)
    def __mul__(self, y):
        if isinstance(y, int):
            return PrimeField(self.x * y, self.l)
        if isinstance(y, PrimeField) and self.l == y.l:
            return PrimeField(self.x * y.x, self.l)
        return NotImplemented

    def __rmul__(self, y):
        if isinstance(y, int):
            return self * y
        return NotImplemented

    # Integer exponentiation
    def __pow__(self, y):
        if isinstance(y, int) and y >= 0:
            return PrimeField(self.x ** y, self.l)
        return NotImplemented

    # Equality
    def __eq__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x == y.x
        raise TypeError

    # Inequality
    def __ne__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x != y.x
        raise TypeError

    # Less-than comparison (does not account for overflow)
    def __lt__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x < y.x
        raise TypeError

    # Greater-than comparison (does not account for overflow)
    def __gt__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x > y.x
        raise TypeError

    # Less-than-or-equal comparison (does not account for overflow)
    def __le__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x <= y.x
        raise TypeError

    # Greater-than-or-equal comparison (does not account for overflow)
    def __ge__(self, y):
        if isinstance(y, PrimeField) and self.l == y.l:
            return self.x >= y.x
        raise TypeError

    # String representation
    def __repr__(self):
        return f'{ self.x } (mod { self.l })'

    # Negation
    def __neg__(self):
        return PrimeField(-self.x, self.l)

class Polynomial:
    pass

# Field of non-prime order l. No prime checking of l
class NonPrimeField:
    pass
