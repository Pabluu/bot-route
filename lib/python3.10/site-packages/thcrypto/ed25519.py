__all__ = ['Ed25519Result', 'Ed25519']

import os
import binascii

from typing import TypeAlias
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from thresult.result import Ok, Err

Ed25519: TypeAlias = 'Ed25519'
Ed25519Result: type = Ok[ed25519.Ed25519PrivateKey | str | bytes | bool] | Err[str]


class Ed25519():

    def __init__(self, private_key: ed25519.Ed25519PrivateKey = None, public_key: object = None):
        assert private_key or public_key
        self.private_key: ed25519.Ed25519PrivateKey = private_key
        self.public_key: ed25519.Ed25519PublicKey = private_key.public_key() if private_key else public_key

    @classmethod
    @Ed25519Result[Ed25519, str]
    def load_or_generate_file(cls, private_path: str = 'sk_ed25519.pem',
                              public_path: str = 'pk_ed25519.pem') -> Ed25519:
        '''
        Load ed25519 keys from file if file not exists then generate keys write them to the file and returns Ed25519
        '''
        if os.path.exists(private_path) and os.path.exists(public_path):
            self: Ed25519 = Ed25519.load(private_path, public_path).unwrap()
            return self
        elif os.path.exists(private_path):  # pragma: no cover
            self: Ed25519 = Ed25519.load(private_path, None).unwrap()
            return self
        elif os.path.exists(public_path):  # pragma: no cover
            self: Ed25519 = Ed25519.load(None, public_path).unwrap()
            return self
        else:
            self: Ed25519 = Ed25519.generate().unwrap()
            self.save(private_path, public_path)
            return self

    @classmethod
    @Ed25519Result[Ed25519, str]
    def generate(cls) -> Ed25519:
        '''
        Generate Ed25519 keys
        '''
        private_key: ed25519.Ed25519PrivateKey = ed25519_generate_private_key().unwrap()
        public_key: ed25519.Ed25519PublicKey = ed25519_get_public_key(private_key).unwrap()
        self: Ed25519 = Ed25519(private_key, public_key)
        return self

    @Ed25519Result[bool, str]
    def save(self, private_path: str, public_path: str) -> bool:
        '''
        Save Ed25519 keys to the specified path
        '''
        ed25519_save_private_key(self.private_key, private_path).unwrap()
        ed25519_save_public_key(self.public_key, public_path).unwrap()

        return True

    @classmethod
    @Ed25519Result[Ed25519, str]
    def load(cls, private_path: str = None, public_path: str = None) -> Ed25519:
        '''
        Load Ed25519 keys from specified path
        '''
        assert private_path or public_path
        private_key: ed25519.Ed25519PrivateKey = ed25519_load_private_key(
            private_path).unwrap() if private_path else None
        public_key: ed25519.Ed25519PublicKey = ed25519_load_public_key(public_path).unwrap() if public_path else None
        self: Ed25519 = Ed25519(private_key, public_key)
        return self

    @Ed25519Result[bytes, str]
    def sign(self, data: bytes) -> bytes:
        '''
        Sign data with ed25519 private key
        '''
        signature: bytes = ed25519_sign(self.private_key, data).unwrap()
        return signature

    @Ed25519Result[bool, str]
    def verify(self, signature: bytes, data: bytes) -> bool:
        '''
        Verify signature with ed25519 public key
        '''
        verify_result: bool = ed25519_verify(self.public_key, signature, data).unwrap()
        return verify_result

    @Ed25519Result[bytes, str]
    def get_raw_private_key_bytes(self) -> bytes:
        '''
        Get serialized bytes of the private key
        '''
        k = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

        # if k is not None and isinstance(k, bytes):
        return k

    @Ed25519Result[str, str]
    def get_raw_private_key(self) -> str:
        '''
        Get serialized bytes of the private key decoded to string
        '''
        k = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

        k = binascii.b2a_hex(k).decode()

        return k

    @Ed25519Result[bytes, str]
    def get_raw_public_key_bytes(self) -> bytes:
        '''
        Get serialized bytes of the public key
        '''
        k = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        return k

    @Ed25519Result[str, str]
    def get_raw_public_key(self) -> str:
        '''
        Get serialized bytes of the public key decoded to string
        '''
        k = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        k = binascii.b2a_hex(k).decode()

        return k


#
# low-level functions
#
@Ed25519Result[ed25519.Ed25519PrivateKey, str]
def ed25519_generate_private_key() -> ed25519.Ed25519PrivateKey:
    '''
    Generate ed25519 private key
    '''
    private_key: ed25519.Ed25519PrivateKey = ed25519.Ed25519PrivateKey.generate()
    return private_key


@Ed25519Result[ed25519.Ed25519PublicKey, str]
def ed25519_get_public_key(private_key: ed25519.Ed25519PrivateKey) -> ed25519.Ed25519PublicKey:
    '''
    Get ed25519 public key from private key
    '''
    public_key: ed25519.Ed25519PublicKey = private_key.public_key()
    return public_key


@Ed25519Result[bool, str]
def ed25519_save_private_key(private_key: ed25519.Ed25519PrivateKey, private_path: str) -> bool:
    '''
    Save ed25519 private key to the file
    '''
    private_pem: bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())

    with open(private_path, 'wb') as f:
        f.write(private_pem)
    return True


@Ed25519Result[bool, str]
def ed25519_save_public_key(public_key: ed25519.Ed25519PublicKey, public_path: str) -> bool:
    '''
    Save ed25519 public key to the file 
    '''
    public_pem: bytes = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PublicFormat.SubjectPublicKeyInfo)
    with open(public_path, 'wb') as f:
        f.write(public_pem)
    return True


@Ed25519Result[ed25519.Ed25519PrivateKey, str]
def ed25519_load_private_key(path: str) -> ed25519.Ed25519PrivateKey:
    '''
    Load ed25519 private key from file 
    '''
    with open(path, 'rb') as f:
        private_pem_data = f.read()

    private_key: ed25519.Ed25519PrivateKey = load_pem_private_key(private_pem_data,
                                                                  password=None,
                                                                  backend=default_backend())
    return private_key


@Ed25519Result[ed25519.Ed25519PublicKey, str]
def ed25519_load_public_key(path: str) -> ed25519.Ed25519PublicKey:
    '''
    Load ed25519 public key from file 
    '''
    with open(path, 'rb') as f:
        public_pem_data = f.read()

    public_key: ed25519.Ed25519PublicKey = load_pem_public_key(public_pem_data, default_backend())
    return public_key


@Ed25519Result[bytes, str]
def ed25519_sign(private_key: ed25519.Ed25519PrivateKey, data: bytes) -> bytes:
    '''
    Sign data with ed25519 private key
    '''
    signature: bytes = private_key.sign(data)
    return signature


@Ed25519Result[bool, str]
def ed25519_verify(public_key: ed25519.Ed25519PublicKey, signature: bytes, data: bytes) -> bool:
    '''
    Verify signature with ed25519 public key
    '''
    public_key.verify(signature, data)
    return True
