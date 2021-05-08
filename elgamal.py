# Elliptic Curve Elgamal encryption

from dumb25519 import *

class ElgamalPublicKey:
    # Set up a public key
    #
    # INPUT
    #   N: public key (Point)
    def __init__(self, N):
        if not isinstance(N, Point):
            raise TypeError('Bad public key!')
        self.N = N

    # Encrypt a message
    #
    # INPUT
    #   M: plaintext message (Point)
    # RETURNS
    #   ciphertext ((Point, Point))
    def encrypt(self, M):
        if not isinstance(M, Point):
            raise TypeError('Bad message!')

        r = random_scalar()   # blinding factor
        return (r * G, M + r * self.N)

class ElgamalPrivateKey:
    # Set up a private key
    #
    # INPUT
    #   x: private key (Scalar)
    def __init__(self, x):
        if not isinstance(x, Scalar):
            raise TypeError('Bad private key!')
        self.x = x

    # Get the public key
    #
    # RETURNS
    #   ElgamalPublicKey instance
    def get_public(self):
        return ElgamalPublicKey(self.x * G)

    # Decryption
    #
    # INPUT
    #   C: ciphertext ((Point, Point))
    # RETURNS
    #   plaintext message (Point)
    def decrypt(self, C):
        if not isinstance(C, tuple):
            raise TypeError('Bad cipher!')
        if not (len(C) == 2 and isinstance(C[0], Point) and isinstance(C[1], Point)):
            raise TypeError('Bad cipher!')

        return C[1] - self.x * C[0]

if __name__ == '__main__':
    # TESTING
    privkey = ElgamalPrivateKey(random_scalar())
    print("Private Key (Scalar): " + repr(privkey.x))
    plaintext = random_point()
    print("Plaintext (Point)   : " + repr(plaintext))
    
    # Encryption
    pubkey = privkey.get_public()
    cipher = pubkey.encrypt(plaintext)
    print("\nCiphertext (Point, Point): " + repr(cipher))
    
    # Decryption
    decrypted = privkey.decrypt(cipher)
    print("\nDecrypted (Point)   : " + repr(decrypted))
    if decrypted == plaintext:
        print("Works like a charm!")
    else:
        print("Plaintext not recovered.")