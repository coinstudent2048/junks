# Elliptic Curve Integrated Encryption Scheme (ECIES)
# Python 3
#
# Modified for use of xmr_keygen.py

import hmac
import hashlib

import dumb25519

# -------- customizable --------
# key-derivation function (KDF)
# inp_key is private
# kdf_extra is public
def KDF(inp_key, kdf_extra):
    pass
    # output MAC key and ENC key separately
    return mac_key, enc_key

# message authentication code (MAC)
# mac_key is shared secret
# cipher is public
# mac_extra is public
def MAC(mac_key, cipher, mac_extra):
    pass
    return tag

# symmetric encryption (ENC)
# text is shared secret
# enc_key is shared secret
def ENC(text, enc_key):
    pass
    return cipher
# -------- customizable --------

# it is assumed that send_privkey is the sender's private key for XMR address
# and recv_pubkey is the receiver's public key for XMR address
def encrypt(plaintext, send_privkey, recv_pubkey, kdf_extra, mac_extra):
    shared_secret_key = (send_privkey * recv_pubkey).x
    mac_key, enc_key = KDF(shared_secret_key, kdf_extra)
    cipher = ENC(plaintext, enc_key)
    tag = MAC(mac_key, cipher, mac_extra)
    return cipher, tag

# it is assumed that send_pubkey is validated (EC point, in main subgroup, etc.)
def decrypt(cipher, tag, recv_privkey, send_pubkey, kdf_extra, mac_extra):
    shared_secret_key = (recv_privkey * send_pubkey).x
    mac_key, enc_key = KDF(shared_secret_key, kdf_extra)
    check_tag = MAC(mac_key, cipher, mac_extra)
    if not compare_digest(check_tag, tag):   # if check_tag != tag (but designed to prevent timing analysis)
        raise ValueError("tag mismatch --> bad cipher!")
    plaintext = ENC(cipher, enc_key)
    return plaintext
