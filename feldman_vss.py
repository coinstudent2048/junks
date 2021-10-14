# Feldman's Verifiable Secret Sharing (Section 4.1 of Gennaro and Goldfeder 's work)
# Python 3
#
# Unoptimized and no error-checking. Coded for clarity instead.

from dumb25519 import *

# polynomial evaluation poly(x)
#    * a_list: list of coefficients
def polynomial(x, a_list):
    powers_x = ScalarVector()
    powers_x.append(Scalar(1))
    for i in range(len(a_list) - 1):
        powers_x.append(x * powers_x[i])
    return powers_x ** ScalarVector(a_list)

class FeldmanVSS:
    # generate share_list (for all n players) and V_list
    #    * secret: Scalar
    #    * player_list: list of x-coords of share points. must have length n >= m
    #    * m: number of players needed to recover secret
    #    * share_list: list of y-coords of share points
    #    * a_list: the secret polynomial
    #    * V_list: a_list * G. used in verification
    def generate(self, secret, player_list, m):
        a_list = [None for _ in range(m)]
        V_list = [None for _ in range(m)]
        for i in range(m):
            if i == 0:
                a_list[0] = secret   # a_0 = secret
            else:
                a_list[i] = random_scalar()
            V_list[i] = a_list[i] * G
        # now generate share_list.
        n = len(player_list)
        share_list = [None for _ in range(n)]
        for i in range(n):
            share_list[i] = polynomial(player_list[i], a_list)
        return share_list, V_list

    # verify share point
    #    * player: x-coord of share point to be verified
    #    * share: y-coord of share point to be verified
    #    * V_list: <secret polynomial> * G. must have length m.
    def verify(self, player, share, V_list):
        LHS = share * G
        powers_player = ScalarVector()
        powers_player.append(Scalar(1))
        for i in range(len(V_list) - 1):
            powers_player.append(player * powers_player[i])
        return LHS == powers_player ** PointVector(V_list)

    # recover secret
    #    * a_player_list: list of x-coords. must have at least length m.
    #    * a_share_list: list of y-coords. must have at least length m.
    def recover(self, a_player_list, a_share_list):
        # Lagrange polynomial interpolation just for a_0
        # Faster polynomial interpolation methods can replace this
        secret = Scalar(0)
        k = len(a_player_list)
        for i in range(k):
            ell = Scalar(1)
            for j in range(k):
                if j != i:
                    ell *= a_player_list[j] * (a_player_list[j] - a_player_list[i]).invert()
            secret += a_share_list[i] * ell
        return secret

if __name__ == '__main__':
    # TESTING
    player_list = [Scalar(1), Scalar(2),   # x-coord for share points. PUBLIC.
                   Scalar(3), Scalar(4)]   # note: these should never be Scalar(0)!
    m = 3   # 3 players needed to recover secret
    n = len(player_list)   # 4 players with shares
    secret = random_scalar()
    print("Secret: " + repr(secret))

    # Phase 1: generating shares
    share_list, V_list = FeldmanVSS().generate(secret, player_list, m)
    # print("Shares:")
    # for i in range(n):
       # print(share_list[i])
    print("--> Phase 1 complete.\n")

    # Phase 2: verification of share point.
    # In this example, player with x-coord Scalar(2) wants to check
    # if share she received is legit. In actual, every player must verify
    # the shares they received.
    if FeldmanVSS().verify(player_list[1], share_list[1], V_list):
        print("WOW! Share is legit.")
    else:
        print("Oh no! Share is not legit. Abort ritual.")
    print("--> Phase 2 complete.\n")

    # Phase 3: recovering the secret.
    # In actual multisig, this shouldn't be done. This is just for verification
    # that secret can be recovered.
    # Test 1: Scalar(1), (3), and (4) will attempt to recover the secret.
    test1_player = [player_list[0], player_list[2], player_list[3]]
    test1_share = [share_list[0], share_list[2], share_list[3]]
    test1_recover = FeldmanVSS().recover(test1_player, test1_share)
    print("Test 1 recovered secret: " + repr(test1_recover))
    if secret == test1_recover:
        print("WOW! Secret recovered!")
    else:
        print("Secret not recovered.")
    # Test 2: Scalar(2), and (4) will attempt to recover the secret.
    test2_player = [player_list[1], player_list[3]]
    test2_share = [share_list[1], share_list[3]]
    test2_recover = FeldmanVSS().recover(test2_player, test2_share)
    print("Test 2 recovered secret: " + repr(test2_recover))
    if secret == test2_recover:
        print("WOW! Secret recovered!")
    else:
        print("Secret not recovered.")
    print("--> Phase 3 complete.")
