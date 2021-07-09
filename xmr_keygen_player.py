# Player for xmr_keygen.py

from dumb25519 import *
# from ecies import *
import itertools
import random
from ast import literal_eval

# generate new point for Round 2. customizable
def round2_new_point(pubkey_list):
    out = random.choice(pubkey_list)
    max_rnd = 1 << 64   # scalar to be multiplied is randomly selected from [0, max_rnd[
    for P in pubkey_list:
        out += Scalar(random.randrange(max_rnd)) * P
    return out

# # alternative: completely new random point
# def round2_new_point():
#     return random_point()

# make tuple from string
def make_tuple(string):
    # in actual, manual parsing
    return literal_eval(string)

# key function for sorting EC points (during Premerge)
def point_sort(ec_point):
    return ec_point.y

class Player:
    def __init__(self, my_id, M):
        self.id = my_id   # player ID (int)
        self.M = M   # threshold
        self.prvkey = random_scalar()
        self.pubkey = self.prvkey * G
        self.others_pubkey = {}

    # receiver of other player's public keys
    def round1_recv(self, other_id, other_pubkey):
        # validate other_pubkey (not implemented here)
        self.others_pubkey[other_id] = other_pubkey

    # prepare for round 2
    def round2_init(self):
        self.others = list(self.others_pubkey.keys())
        self.tuple_len = len(self.others) - self.M + 2
        # 'self.others + [self.id]' must be sorted for easier round3_init
        self.combs = list(itertools.combinations(sorted(self.others + [self.id]), self.tuple_len))
        self.share_points = {}   # dict of share EC points
        self.send_round2 = {j: {} for j in self.others}   # data to send per player

        pubkey_list = list(self.others_pubkey.values())
        for comb in self.combs:
            if self.id in comb:
                self.share_points[comb] = round2_new_point(pubkey_list)   # add to dict

        for i in self.others:
            data_enc = {}   # temp location of data to encrypt
            for comb in self.combs:
                if i in comb and self.id in comb:
                    data_enc[str(comb)] = str(self.share_points[comb])   # add to dict   
            # data_enc must be encrypted thru ECIES, but me lazy, so encryption not executed for now
            self.send_round2[i]['id'] = self.id
            self.send_round2[i]['cipher'] = data_enc
            del(data_enc)
            # then convert send_round2[j] to JSON or then maybe base64 (not implemented here)

    # receiver of other player's contribution to share private keys
    def round2_recv(self, recv_round2):
        # parse JSON (not implemented here)
        # recv_round2 must be decrypted thru ECIES, but me lazy, so decryption not executed for now
        send_id = recv_round2['id']
        cipher = recv_round2['cipher']
        # validate other's shared EC points (not implemented here for now)
        for comb in cipher:
            # raise error if comb is invalid (i.e. not in share_points)
            self.share_points[make_tuple(comb)] += Point(cipher[comb])

    # prepare for round 3
    def round3_init(self):
        del(self.send_round2)
        self.share_prvkey = {}   # dict of share private keys
        self.share_pubkey = {}   # dict of share public keys
        self.send_round3 = {}   # basically share_pubkey + id (same to all others)
        for comb in self.combs:
            if self.id in comb:
                self.share_prvkey[comb] = hash_to_scalar(self.share_points[comb])
                self.share_pubkey[comb] = self.share_prvkey[comb] * G
        del(self.share_points)
        # it is not required for share_pubkey to be encrypted thru ECIES
        self.send_round3['id'] = self.id
        self.send_round3['pubkeys'] = self.share_pubkey

    # receiver of addeds for the final multisig public key
    def round3_recv(self, recv_round3):
        # parse JSON (not implemented here)
        send_id = recv_round3['id']
        pubkeys = recv_round3['pubkeys']
        for comb in pubkeys:
            if not comb in self.share_pubkey:
                self.share_pubkey[comb] = pubkeys[comb]
            else:
                # public keys of the same comb MUST be the same! 
                if self.share_pubkey[comb] != pubkeys[comb]:
                    raise ValueError("public key for {} from {} conflicts with old public key".format(comb, send_id))

    # final: premerge the share private and public keys and get the final multisig public key
    def final(self):
        sorted_share_pubkey = sorted(self.share_pubkey.values(), key = point_sort)
        self.multisig_pubkey = Z
        for comb in self.combs:
            premerge = hash_to_scalar('premerge', sorted_share_pubkey, self.share_pubkey[comb])
            if self.id in comb:
                self.share_prvkey[comb] *= premerge
            self.multisig_pubkey += self.share_pubkey[comb] * premerge
        del(self.share_pubkey)
