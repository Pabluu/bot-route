__all__ = ['SECP256K1Result', 'SECP256K1']

import os

from typing import TypeAlias
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from thresult.result import Ok, Err


SECP256K1: TypeAlias = 'SECP256K1'
SECP256K1Result: type = Ok[str | bytes | bool | ec.EllipticCurvePrivateKey | ec.EllipticCurvePublicKey] | Err[str]


class SECP256K1():
    private_key: ec.EllipticCurvePrivateKey | None = None
    public_key: ec.EllipticCurvePublicKey | None = None

    def __init__(self, private_key: ec.EllipticCurvePrivateKey=None, public_key: ec.EllipticCurvePublicKey=None):
        assert private_key or public_key
        self.private_key = private_key
        self.public_key = private_key.public_key() if private_key else public_key


    @classmethod
    @SECP256K1Result[SECP256K1, str]
    def load_or_generate_file(cls, private_path: str='sk_secp256k1.pem', public_path: str='pk_secp256k1.pem') -> SECP256K1:
        '''
        Load SECP256K1 keys from file if file not exists then generate keys write them to the file and returns Ed25519
        '''
        if os.path.exists(private_path) and os.path.exists(public_path):
            self: SECP256K1 = SECP256K1.load(private_path, public_path).unwrap()
            return self
        elif os.path.exists(private_path):  # pragma: no cover
            self: SECP256K1 = SECP256K1.load(private_path, None).unwrap() 
            return self
        elif os.path.exists(public_path):  # pragma: no cover
            self: SECP256K1 = SECP256K1.load(None, public_path).unwrap() 
            return self
        else:
            self: SECP256K1 = SECP256K1.generate().unwrap()
            self.save(private_path, public_path)
            return self


    @classmethod
    @SECP256K1Result[SECP256K1, str]
    def generate(cls) -> SECP256K1:
        '''
        Generate SECP256K1 keys
        '''
        private_key: ec.EllipticCurvePrivateKey = secp256k1_generate_private_key().unwrap()
        public_key: ec.EllipticCurvePublicKey = secp256k1_get_public_key(private_key).unwrap()
        self = SECP256K1(private_key, public_key)
        return self


    @SECP256K1Result[bool, str]
    def save(self, private_path: str, public_path: str) -> bool:
        '''
        Save SECP256K1 keys to the specified path
        '''
        secp256k1_save_private_key(self.private_key, private_path).unwrap()
        secp256k1_save_public_key(self.public_key, public_path).unwrap()
        return True


    @classmethod
    @SECP256K1Result[SECP256K1, str]
    def load(cls, private_path: str=None, public_path: str=None)  -> SECP256K1:
        '''
        Load SECP256K1 keys from specified path
        '''
        assert private_path or public_path
        private_key: ec.EllipticCurvePrivateKey = secp256k1_load_private_key(private_path).unwrap() if private_path else None
        public_key: ec.EllipticCurvePublicKey = secp256k1_load_public_key(public_path) if public_path else None
        self: SECP256K1 = SECP256K1(private_key, public_key)
        return self


    @SECP256K1Result[bytes, str]
    def sign(self, data: bytes) -> bytes:
        '''
        Sign data with SECP256K1 private key
        '''
        sign_in_res: bytes = secp256k1_sign(self.private_key, data).unwrap()
        return sign_in_res


    @SECP256K1Result[bool, str]
    def verify(self, signature: bytes, data: bytes) -> bool:
        '''
        Verify signature with SECP256K1 public key
        '''
        b: bool = secp256k1_verify(self.public_key, signature, data).unwrap()
        return b


#
# low-level functions
#
@SECP256K1Result[ec.EllipticCurvePrivateKey, str]
def secp256k1_generate_private_key() -> ec.EllipticCurvePrivateKey:
    '''
    Generate SECP256K1 private key
    '''
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    return private_key


@SECP256K1Result[ec.EllipticCurvePublicKey, str]
def secp256k1_get_public_key(private_key: ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
    '''
    Get SECP256K1 public key from private key
    '''
    public_key: ec.EllipticCurvePublicKey = private_key.public_key()
    return public_key


@SECP256K1Result[bool, str]
def secp256k1_save_private_key(private_key: ec.EllipticCurvePrivateKey, private_path: str) -> bool:
    '''
    Save SECP256K1 private key to the file
    '''
    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                            format=serialization.PrivateFormat.PKCS8,
                                            encryption_algorithm=serialization.NoEncryption())
    with open(private_path, 'wb') as f:  
        f.write(private_pem)
    return True
    
         
@SECP256K1Result[bool, str]
def secp256k1_save_public_key(public_key: ec.EllipticCurvePublicKey, public_path: str) -> bool:
    '''
    Save SECP256K1 public key to the file 
    '''
    public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PublicFormat.SubjectPublicKeyInfo)
    with open(public_path, 'wb') as f:
        f.write(public_pem)
    return True


@SECP256K1Result[ec.EllipticCurvePrivateKey, str]
def secp256k1_load_private_key(path: str) -> ec.EllipticCurvePrivateKey:
    '''
    Load SECP256K1 private key from file 
    '''
    with open(path, 'rb') as f:
        private_pem_data = f.read()

    private_key: ec.EllipticCurvePrivateKey = load_pem_private_key(private_pem_data, None, default_backend())
    return private_key


@SECP256K1Result[ec.EllipticCurvePublicKey, str]
def secp256k1_load_public_key(path: str) -> ec.EllipticCurvePublicKey:
    '''
    Load SECP256K1 public key from file 
    '''
    with open(path, 'rb') as f:
        public_pem_data = f.read()

    public_key: ec.EllipticCurvePublicKey = load_pem_public_key(public_pem_data, default_backend())
    return public_key


@SECP256K1Result[bytes, str]
def secp256k1_sign(private_key: ec.EllipticCurvePrivateKey, data: bytes) -> bytes:
    '''
    Sign data with SECP256K1 private key
    '''
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    signature: bytes = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    return signature
    
   
@SECP256K1Result[bool, str]
def secp256k1_verify(public_key: ec.EllipticCurvePublicKey, signature: bytes, data: bytes) -> bool:
    '''
    Verify signature with SECP256K1 public key
    '''  
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
    return True
