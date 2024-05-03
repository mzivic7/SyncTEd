from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def gen_key():
    """Generate RSA keypair"""
    priv_key = RSA.generate(2048)
    pub_key = priv_key.publickey()
    priv_pem = priv_key.export_key().decode()
    pub_pem = pub_key.export_key().decode()
    with open("data/private_key.pem", 'w') as priv:
        priv.write(priv_pem)
    with open("data/public_key.pem", 'w') as pub:
        pub.write(pub_pem)
    return pub_key, priv_key


def encrypt(plaintext, peer_pub_key):
    """Encrypt with RSA"""
    cipher = PKCS1_OAEP.new(key=peer_pub_key)
    cipher_text = cipher.encrypt(plaintext.encode())
    return cipher_text


def decrypt(cipher_text, priv_key):
    """Decrypt with RSA"""
    decrypt = PKCS1_OAEP.new(key=priv_key)
    plaintext = decrypt.decrypt(cipher_text).decode()
    return plaintext
