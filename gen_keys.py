from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

priv_key = RSA.generate(1024)   # generate private key
pub_key = priv_key.publickey()   # generate public key from private

priv_pem = priv_key.export_key().decode()   # convert private key to string
pub_pem = pub_key.export_key().decode()   # convert public key to string

with open("data/priv_key.pem", 'w') as priv:   # write keys to pem files
    priv.write(priv_pem)
with open("data/pub_key.pem", 'w') as pub:
    pub.write(pub_pem)
