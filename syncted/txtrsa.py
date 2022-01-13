from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# generate RSA keypair
def gen_key():
    priv_key = RSA.generate(2048)   # generate private key with size
    pub_key = priv_key.publickey()   # generate public key from private
    priv_pem = priv_key.export_key().decode()   # convert private key to string
    pub_pem = pub_key.export_key().decode()   # convert public key to string
    with open("data/private_key.pem", 'w') as priv:   # write keys to pem files
        priv.write(priv_pem)
    with open("data/public_key.pem", 'w') as pub:
        pub.write(pub_pem)
    return pub_key, priv_key

# RSA encryption
def enc(plaintext, peer_pub_key):
    cipher = PKCS1_OAEP.new(key=peer_pub_key)   # prepare for encryption with key
    cipher_text = cipher.encrypt(plaintext.encode())   # encrypt data
    return cipher_text

# RSA decryption
def dec(cipher_text, priv_key):
    decrypt = PKCS1_OAEP.new(key=priv_key)   # prepare for decryption with key
    plaintext = decrypt.decrypt(cipher_text).decode()   # decrypt data
    return plaintext
