# A Constant Communication Round Arbitrary Treshold Key Generation for Monero
# Python 2
#
# WARNING: Security against any attack model yet to be proven.
# TODO: Replace Elgamal with ECIES, because we don't need homomorphicity.

from dumb25519 import *
from elgamal import *
import itertools
import random

# primitive random.choices (with replacement)
def choices(population, k=1):
    out = []
    for i in range(k):
        out += [random.choice(population)]
    return out

# We setup a 3-of-6 'multisig' (wallet-level)
N = 6
M = 3
# Initial: keypairs of each player
players = range(N)
prvkeys = [None for _ in players]
pubkeys = [None for _ in players]
round2_recv = [[None for _ in players] for _ in players]   # players received data in Round 2
for i in players:
    prvkeys[i] = random_scalar()
    pubkeys[i] = prvkeys[i] * G

# Round 1: send public keys to other players
# We just assume here that it is completed.
print('Phase 1 completed: public keys sent to other players.\n')

# Round 2: construction of share private keys
comb_data = [None for _ in players]   # players generated data per combination. will be list of dict
for i in players:
    # -------- relevant code to be put in wallet begins --------
    others = [j for j in players if j != i]   # players\{i}
    others_comb = list(itertools.combinations(others, N - M))   # N-1 choose N-M combinations
    comb_data[i] = {}   # data to send per combination
    others_data = [[] for _ in players]   # encrypted (via Elgamal) data to send to others

    for comb in others_comb:
        # Note for next line: itertools.combinations returns list of tuples, dict keys need to be
        # immutable (e.g. tuple), and sorting is so that summing after Elgamal decryption is easier.
        comb_with_i = tuple(sorted(list(comb) + [i]))   # add i in the comb.
        # Note for next lines: in fact, comb_data[i][comb_with_i] could be ANY element of the main subgroup!
        # so now I like it to be a sum of randomly chosen public keys (NOT i) times player i's private key.
        comb_data[i][comb_with_i] = Z   # identity element
        max_addends = N - 1   # freely adjustable
        for k in choices(others, random.randint(1, max_addends)):
            comb_data[i][comb_with_i] += prvkeys[i] * pubkeys[k]
        # packaging data to send to players in the combination
        for k in comb:
            # encrypt comb_data[i][j] using pubkeys[k] 
            enc = ElgamalPublicKey(pubkeys[k]).encrypt(comb_data[i][comb_with_i])
            others_data[k] += [(comb_with_i, enc)]
    # 'send' data to others now!
    for j in others:
        round2_recv[j][i] = others_data[j]
    # -------- relevant code to be put in wallet ends --------
    print('Player ' + str(i) + ' sent data to other players')

# Example: this is what player 0 would send to player 5
print('\nThis is the data player 0 would send to player 5:\n' + repr(round2_recv[5][0]) + '\n')

# After the sending, each player should now construct the share private keys
# Note: comb_data[i] will be reused for computations, but...
share_prvkeys = [None for _ in players]   # share private keys are stored here. will be list of dict
for i in players:
    # -------- relevant code to be put in wallet begins --------
    others = [j for j in players if j != i]   # players\{i}
    for j in others:
        # Unimplemented here, but important in production:
        # 1) Raise ALARM if parsing of received data fails!
        # 2) After decrypting Elgamal, raise ALARM if not in elliptic curve!
        # 3) If in curve, multiply it by cofactor to force it in the main subgroup.
        for comb, enc in round2_recv[i][j]:
            # decrypt Elgamal
            dec = ElgamalPrivateKey(prvkeys[i]).decrypt(enc)
            # ...and add it to comb_data[i]
            comb_data[i][comb] += dec
    # do the final hash_to_scalar()
    share_prvkeys[i] = {}   # share private keys for player i
    for comb, sum in comb_data[i].items():
        share_prvkeys[i][comb] = hash_to_scalar(sum)
    # -------- relevant code to be put in wallet ends --------
    print('Player ' + str(i) + '\'s share private keys:\n' + repr(share_prvkeys[i]))
    
print('Phase 2 completed: share private keys constructed.\n')

# Round 3: send their share public keys to other players
share_pubkeys = {}   # dict of share public keys
for i in players:
    # -------- relevant code to be put in wallet begins --------
    # Unimplemented here, but important in production:
    # 1) Raise ALARM if parsing of received data fails!
    # 2) Raise ALARM if you received different pubkeys for same comb!
    for comb, key in share_prvkeys[i].items():
        a_pubkey = key * G
        if not comb in share_pubkeys:   # add a_pubkey in list IF its comb is not there yet
            share_pubkeys[comb] = a_pubkey
    # -------- relevant code to be put in wallet ends --------

print('Share Public Keys:\n' + str(share_pubkeys))
agg_pubkeys = sorted(share_pubkeys.values())   # for premerge
multisig_pubkey = Z
for i in agg_pubkeys:
    multisig_pubkey += hash_to_scalar('premerge', agg_pubkeys, i) * i
print('\n***MULTISIG PUBLIC KEY (Sum)***: ' + repr(multisig_pubkey))
print('Phase 3 completed: share public keys sent to other players.\n')

# TESTING
# For example, players 1, 2, & 5 will recover the multisig private key (round-robin)
print('For testing, players 1, 2, & 5 will recover the multisig private key.')
recov_prvkey = Scalar(0)   # multisig private key to recover
signer_0 = 1
signer_1 = 2
signer_2 = 5

# -------- relevant code to be put in wallet begins --------
# first player signing
for comb, key in share_prvkeys[signer_0].items():
    recov_prvkey += hash_to_scalar('premerge', agg_pubkeys, key * G) * key   # add all

# second player signing
for comb, key in share_prvkeys[signer_1].items():
    if not signer_0 in comb:   # remove keys with 1st player in it
        recov_prvkey += hash_to_scalar('premerge', agg_pubkeys, key * G) * key   # add all

# third player signing
for comb, key in share_prvkeys[signer_2].items():
    if not signer_0 in comb and not signer_1 in comb:   # remove keys with 1st & 2nd player in it
        recov_prvkey += hash_to_scalar('premerge', agg_pubkeys, key * G) * key   # add all
# -------- relevant code to be put in wallet ends --------

print('\n***RECOVERED PRIVATE KEY***: ' + repr(recov_prvkey))
recov_pubkey = recov_prvkey * G
print('***RECOVERED PUBLIC  KEY***: ' + repr(recov_pubkey))
# THE ULTIMATE TEST
if multisig_pubkey == recov_pubkey:
    print('Private key successfully recovered!!!')
else:
    print('Private key recovery failed :(')