from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from ourJWT import OUR_class, OUR_exception


def keygen():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_bytes.decode(), pem


PRIVKEY, PUBKEY = keygen()


encoder: OUR_class.Encoder
OUR_class.Decoder.pub_key = PUBKEY

try:
    encoder = OUR_class.Encoder(PRIVKEY)
    print("created both encoder and decoder object")
except OUR_exception.NoKey:
    print("NO KEY ERROR")
    exit()
