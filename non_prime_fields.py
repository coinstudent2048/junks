# Construction of Non-prime fields
# Python 3
#
# Minimal optimization and error-checking. Coded for clarity instead.


# Field of prime order l. No prime checking of l
class PrimeField:
    def __init__(self, x, l):
        if isinstance(x, int) and isinstance(l, int) and l > 0:
            self.x = x % l
            self.l = l
        else:
            raise TypeError

    # Multiplicative inversion
    def invert(self):
        if self.x == 0:
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
        return self.__mul__(-1)


# Polynomial here is a list of PrimeField of order l [c0, c1, ..., cN]
# which means c0 + c1 * x + ... + cN * x ** N (mod l)
class Polynomial:
    def __init__(self, coeffs, l):
        if isinstance(coeffs, list) and isinstance(l, int) and l > 0:
            first_trail_zero = 1
            for i, j in enumerate(coeffs):
                if not (isinstance(j, PrimeField) and j.l == l):
                    raise TypeError
                if i > 0 and j.x != 0:
                    first_trail_zero = i + 1
            self.coeffs = coeffs[0: first_trail_zero] # remove trailing zeros
            self.l = l
        else:
            raise TypeError

    # Addition
    def __add__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            if len(self.coeffs) > len(y.coeffs):
                extra_coeffs = self.coeffs[len(y.coeffs): len(self.coeffs)]
            else:
                extra_coeffs = y.coeffs[len(self.coeffs): len(y.coeffs)]
            return Polynomial([i + j for i, j in zip(self.coeffs, y.coeffs)] + extra_coeffs, self.l)
        return NotImplemented

    # Subtraction
    def __sub__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            if len(self.coeffs) > len(y.coeffs):
                extra_coeffs = self.coeffs[len(y.coeffs): len(self.coeffs)]
            else:
                extra_coeffs = [-i for i in y.coeffs[len(self.coeffs): len(y.coeffs)]]
            return Polynomial([i - j for i, j in zip(self.coeffs, y.coeffs)] + extra_coeffs, self.l)
        return NotImplemented

    # Multiplication (possibly by an integer)
    def __mul__(self, y):
        if isinstance(y, int):
            return Polynomial([i * y for i in self.coeffs], self.l)
        if isinstance(y, Polynomial) and self.l == y.l:
            # this is naive algorithm
            zero_coeffs = [PrimeField(0, self.l)]
            product = zero_coeffs * (len(self.coeffs) + len(y.coeffs) - 1)
            for i0, j0 in enumerate(self.coeffs):
                for i1, j1 in enumerate(y.coeffs):
                    product[i0 + i1] += j0 * j1
            return Polynomial(product, self.l)
        return NotImplemented

    def __rmul__(self, y):
        if isinstance(y, int):
            return self * y
        return NotImplemented

    # Divmod (Euclidean division)
    def divmod(self, y, mod_only=False):
        if isinstance(y, Polynomial) and self.l == y.l:
            # this is naive algorithm
            zero_coeffs = [PrimeField(0, self.l)]
            if y.coeffs == zero_poly:
                raise ZeroDivisionError
            modulo = self
            len_diff = len(modulo.coeffs) - len(y.coeffs)
            if not mod_only:
                quotient = zero_coeffs * (len_diff + 1)

            while len_diff >= 0:
                quot_coeff = modulo.coeffs[-1] * y.coeffs[-1].invert()
                if not mod_only:
                    quotient[len_diff] = quot_coeff
                diff_list = [i - quot_coeff * j for i, j in zip(modulo.coeffs[len_diff: len(modulo.coeffs)], y.coeffs)]
                modulo = Polynomial(modulo.coeffs[0: len_diff] + diff_list, self.l) # utilize remove trailing zeros
                len_diff = len(modulo.coeffs) - len(y.coeffs)
                if modulo.coeffs == zero_coeffs:
                    len_diff -= 1 # here, zero polynomial has 'length' 0

            if mod_only:
                return None, modulo
            else:
                return Polynomial(quotient, self.l), modulo
        return NotImplemented

    # Integer exponentiation
    def __pow__(self, y):
        if isinstance(y, int) and y >= 0:
            if y == 0:
                return Polynomial([PrimeField(1, self.l)], self.l)
            Q = self.__pow__(y // 2)
            Q = Q.__mul__(Q)
            if y & 1:
                Q = self.__mul__(Q)
            return Q
        return NotImplemented

    # Equality
    def __eq__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            return self.coeffs == y.coeffs
        raise TypeError

    # Inequality
    def __ne__(self,y):
        if isinstance(y, Polynomial) and self.l == y.l:
            return self.coeffs != y.coeffs
        raise TypeError

    # Less-than comparison. This will be the basis for other comparison dunders
    # This is based on degree of polynomial and ordering of underlying PrimeField
    def __lt__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            if len(self.coeffs) != len(y.coeffs):
                return len(self.coeffs) < len(y.coeffs)
            for i, j in zip(self.coeffs, y.coeffs):
                if i != j:
                    return i < j
            return False # this means that self == y
        raise TypeError

    # Greater-than comparison
    def __gt__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            return not (self.__lt__(y) or self.__eq__(y))
        raise TypeError

    # Less-than-or-equal comparison
    def __le__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            return self.__lt__(y) or self.__eq__(y)
        raise TypeError

    # Greater-than-or-equal comparison
    def __ge__(self, y):
        if isinstance(y, Polynomial) and self.l == y.l:
            return not self.__lt__(y)
        raise TypeError

    # String representation
    def __repr__(self):
        return f'{ [i.x for i in self.coeffs] } (mod { self.l })'

    # Negation
    def __neg__(self):
        return self.__mul__(-1)


def zero_poly(l):
    return Polynomial([PrimeField(0, l)], l)


def one_poly(l):
    return Polynomial([PrimeField(1, l)], l)


# Field of non-prime order defined using irreducible polynomial p. No checking of irreducibility
class NonPrimeField:
    def __init__(self, x, p):
        if isinstance(x, Polynomial) and isinstance(p, Polynomial) and x.l == p.l:
            _, self.x = x.divmod(p, True)
            self.p = p
        else:
            raise TypeError

    # Multiplicative inversion
    def invert(self):
        zero_poly_npf = zero_poly(self.p.l)
        if self.x == zero_poly_npf:
            raise ZeroDivisionError
        # source: https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Simple_algebraic_field_extensions
        # retrieved: 10/03/2023
        t = zero_poly_npf
        newt = one_poly(self.p.l)
        r = self.p
        newr = self.x

        while newr != zero_poly_npf:
            quot, rem = r.divmod(newr)
            r, newr = newr, rem
            t, newt = newt, t - quot * newt

        if len(r.coeffs) > 1:
            raise ValueError("Either self.p is not irreducible or self.x is a multiple of self.p.")

        if self.p.l > 2:
            return NonPrimeField(Polynomial([r.coeffs[0].invert()], self.p.l) * t, self.p)
        else: # optimization
            return NonPrimeField(t, self.p)

    # Addition
    def __add__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return NonPrimeField(self.x + y.x, self.p)
        return NotImplemented

    # Subtraction
    def __sub__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return NonPrimeField(self.x - y.x, self.p)
        return NotImplemented

    # Multiplication (possibly by an integer or a polynomial mod l)
    def __mul__(self, y):
        if isinstance(y, int) or isinstance(y, Polynomial) and self.p.l == y.l:
            return NonPrimeField(self.x * y, self.p)
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return NonPrimeField(self.x * y.x, self.p)
        return NotImplemented

    def __rmul__(self, y):
        if isinstance(y, int) or isinstance(y, Polynomial) and self.p.l == y.l \
        or isinstance(y, Polynomial) and self.p.l == y.l:
            return self * y
        return NotImplemented

    # Integer exponentiation
    def __pow__(self, y):
        if isinstance(y, int) and y >= 0:
            return NonPrimeField(self.x ** y, self.p)
        return NotImplemented

    # Equality
    def __eq__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x == y.x
        raise TypeError

    # Inequality
    def __ne__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x != y.x
        raise TypeError

    # Less-than comparison
    def __lt__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x < y.x
        raise TypeError

    # Greater-than comparison
    def __gt__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x > y.x
        raise TypeError

    # Less-than-or-equal comparison
    def __le__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x <= y.x
        raise TypeError

    # Greater-than-or-equal comparison
    def __ge__(self, y):
        if isinstance(y, NonPrimeField) and self.p == y.p:
            return self.x >= y.x
        raise TypeError

    # String representation
    def __repr__(self):
        return f'{ [i.x for i in self.x.coeffs] } (mod { self.p })'

    # Negation
    def __neg__(self):
        return self.__mul__(-1)
