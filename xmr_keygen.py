# A Constant Communication Round Arbitrary Treshold Key Generation for Monero
# Python 3
#
# Security against any attack model yet to be proven.

import dumb25519
from xmr_keygen_player import Player

# we setup a 3-of-6 'multisig' (wallet-level)
N = 6
M = 3
# Initial: init each player
players = range(N)
players_class = [None for _ in players]
for i in players:
    players_class[i] = Player(i, M)

# Round 1: send public keys to other players
for i in players:
    for j in players:
        if i != j:
            players_class[j].round1_recv(i, players_class[i].pubkey)
print('Round 1 completed: public keys sent to other players.\n')

# Round 2: construction of share private keys
for i in players:
    players_class[i].round2_init()

for i in players:
    for j in players:
        if i != j:
            players_class[j].round2_recv(players_class[i].send_round2[j])
print('Round 2 completed: share private keys constructed.\n')

# Round 3: send their share public keys to other players
for i in players:
    players_class[i].round3_init()

for i in players:
    for j in players:
        if i != j:
            players_class[j].round3_recv(players_class[i].send_round3)

print('Round 3 completed: share public keys sent to other players.\n')

# Finalize: Premerge
for i in players:
    players_class[i].final()

print("Share Private Keys of Player 0 (with Premerge):")
for i in players_class[0].share_prvkey:
    print(i, players_class[0].share_prvkey[i])
print("\nFinal Multisig Public Key:", players_class[5].multisig_pubkey)

# Testing: for example, players 1, 2, & 5 will recover the multisig private key (round-robin)
recov_prvkey = dumb25519.Scalar(0)
signer_0 = 1
signer_1 = 2
signer_2 = 5

# first player signing
for comb, key in players_class[signer_0].share_prvkey.items():
    recov_prvkey += key

# second player signing
for comb, key in players_class[signer_1].share_prvkey.items():
    if not signer_0 in comb:
        recov_prvkey += key

# third player signing
for comb, key in players_class[signer_2].share_prvkey.items():
    if not signer_0 in comb and not signer_1 in comb:
        recov_prvkey += key

print("\nRecovered Private Key:", recov_prvkey)
recov_pubkey = recov_prvkey * dumb25519.G
print("Recovered Public Key:", recov_pubkey)
# the ultimate test
if players_class[4].multisig_pubkey == recov_pubkey:
    print("Private key successfully recovered!!!")
else:
    print("Private key recovery failed :(")
