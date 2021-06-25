# Feldman's Verifiable Secret Sharing (Section 4.1 of Gennaro and Goldfeder 's work)
# Python 3
#
# Unoptimized and no error-checking. Coded for clarity instead.

from dumb25519 import *

# polynomial in field F_q
#    * a_0 = secret.
def polynomial(x, a_list):
    p = Scalar(0)
    for i, a_i in enumerate(a_list):
        p += a_i * (x ** i)   # i is int, not Scalar
    return p

class FeldmanVSS:
    # generate share_list (for all n) and V_list
    #    * secret is Scalar in F_q
    #    * player_list is the x-coord of share points. must have length n >= m.
    #    * share_list is the list of y-coords of share points.
    #    * V_list is a_list * G.
    def generate(self, secret, player_list, m):
        # now, generate a_list and V_list
        # Note: a_list is PRIVATE, while V_list is PUBLIC
        a_list = [None for _ in range(m)]
        V_list = [None for _ in range(m)]
        for i in range(m):
            if i == 0:
                a_list[0] = secret   # a_0 = secret
            else:
                a_list[i] = random_scalar()
            V_list[i] = a_list[i] * G
        # now, generate share_list.
        n = len(player_list)
        share_list = [None for _ in range(n)]
        for i in range(n):
            share_list[i] = polynomial(player_list[i], a_list)
        return share_list, V_list

    # verify share
    #    * V_list has length m
    #    * 'share' here is only the y-coord of share point to be verified
    #    * 'player' here is the corresponding x-coord
    def verify(self, player, share, V_list):
        LHS = share * G
        RHS = Z   # identity element of cyclic group
        m = len(V_list)
        for i in range(m):
            RHS += (player ** i) * V_list[i]
        return LHS == RHS

    # recover secret
    #    * a_share_list must have at least length m
    #      for successful recovery
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
