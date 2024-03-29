# Demo of "Key Image Bug"
# Source: https://www.getmonero.org/2017/05/17/disclosure-of-a-major-bug-in-cryptonote-based-currencies.html

import dumb25519

# Generator for the small subgroup of size of the cofactor = 8
# Source: https://monero.stackexchange.com/a/8672
G_small = dumb25519.Point('c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac03fa')

# Aim: double spend!

# Let's say you are an attacker, and you have your key image.
# Key images are in main subgroup, as random_point always outputs.
key_image = dumb25519.random_point()

# For your attack to be possible, make sure that somewhere in tx verification,
# your key image will be multiplied to a Scalar that is a multiple of cofactor = 8.
# Since you initiate the tx, you can always check, but you cannot always choose
# the Scalar. Instead, you try producing proofs again and again until getting the
# desired Scalar. Thanks to "non-interactive" proof, producing proofs do not
# require verifier interaction ;)
tx_ver_scalar = dumb25519.Scalar(1)
while tx_ver_scalar % 8 != dumb25519.Scalar(0):
    tx_ver_scalar = dumb25519.random_scalar()

# Ok you check that the attack is possible. Let's now create 7 more fake key images!
ki_list = []

for i in range(dumb25519.cofactor):
    ki_new = dumb25519.Scalar(i) * G_small + key_image
    print(f'Key image #{ i }: { ki_new }')   # Key image #0 is your original key_image
    ki_list.append(ki_new)

# Are they unique to each other?
ki_set = set([str(i) for i in ki_list])
print(f'Distinct key images: { len(ki_set) }\n')

# So you initiated 8 tx's. Same coins, different "key images".
# Now the verifiers check the tx's. Somewhere there, tx_ver_scalar is being multiplied
# to your 8 "key images"
prod_list = [i * tx_ver_scalar for i in ki_list]

# Let's take a look
print('After multiplying a Scalar that is a multiple of cofactor = 8 to the key images...')
for i, j in enumerate(prod_list):
    print(f'Product point #{ i }: { j }')

# Are they unique to each other?
prod_set = set([str(i) for i in prod_list])
print(f'Distinct product points: { len(prod_set) }\n')

if len(prod_set) == 1:
    print('Theoretical double spend (actually "8 times" spend) committed successfully!!!\n')

# How to mitigate this?
# The most elegant and general solution is to use Ristretto (https://ristretto.group/).
# For Monero, there is a simpler solution. To quote from the getmonero.org source above:
#
#     To mitigate, check key images for correctness by multiplying by the curve order l.
#     Check that the result is the identity element.
#
# Let's do this for ki_list.
check_list = [dumb25519.Scalar('l') * i for i in ki_list]

# Let's take a look
print('After multiplying the curve order l to the key images...')
for i, j in enumerate(check_list):
    print(f'Product point #{ i }: { j } => { j == dumb25519.Z }')

print('Only the #0, corresponding to the original key_image, is the TRUE key image!')

# See https://github.com/monero-project/monero/pull/1744/commits/d282cfcc46d39dc49e97f9ec5cedf7425e74d71f#diff-1fb58b51f281d178c1a564bccf94bc813261a1fd585a9372e3d53999a25f9a53R714
# for the actual mitigation in Monero
