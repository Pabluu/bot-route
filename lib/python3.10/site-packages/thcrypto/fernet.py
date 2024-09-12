__all__ = ['FernetResult', 'Fernet']

import os
import json
import pickle

from typing import TypeAlias
from cryptography.fernet import Fernet as _Fernet

from thresult.result import Ok, Err


Fernet: TypeAlias = 'Fernet'
FernetResult: type = Ok[bytes | str | dict] | Err[str]


class Fernet():
    def __init__(self, fernet: _Fernet | None=None):
        self.fernet: _Fernet = fernet


    @classmethod
    @FernetResult[Fernet, str]
    def generate(cls) -> Fernet:
        '''
        Generate fernet key
        '''
        fernet: _Fernet = fernet_key_generate().unwrap()
        self: Fernet = Fernet(fernet)
        return self


    @classmethod
    @FernetResult[Fernet, str]
    def load_or_generate_file(cls, path: str='fernet.key') -> Fernet:
        '''
        Load fernet key from file, if key not exists, generate key and write it to the file and return fernet key
        '''
        fernet: _Fernet = fernet_key_from_or_generate_file(path).unwrap()
        self: Fernet = Fernet(fernet)
        return self
        

    @FernetResult[bytes, str]
    def encrypt_bytes(self, data_bytes: bytes, current_time: int | None=None) -> bytes:
        '''
        Encrypt bytes with fernet key
        '''
        encrypted_bytes: bytes = fernet_key_encrypt_bytes(self.fernet, data_bytes, current_time).unwrap()
        return encrypted_bytes


    @FernetResult[bytes, str]
    def decrypt_bytes(self, enc_data_bytes: bytes, ttl: int | None=None, current_time: int | None=None) -> bytes:
        '''
        Decrypt bytes with fernet key
        '''
        decrypted_bytes: bytes = fernet_key_decrypt_bytes(self.fernet, enc_data_bytes, ttl, current_time).unwrap()
        return decrypted_bytes


    @FernetResult[str, str]
    def encrypt_dict(self, data_dict: dict, current_time: int | None=None) -> str:
        '''
        Encrypt dict with fernet key
        '''
        encrypted_dict: str = fernet_key_encrypt_dict(self.fernet, data_dict, current_time).unwrap()
        return encrypted_dict


    @FernetResult[dict, str]
    def decrypt_dict(self, enc_data_str: str, ttl: int | None=None, current_time: int | None=None) -> dict:
        '''
        Decrypt dict with fernet key
        '''
        decrypted_dict: dict = fernet_key_decrypt_dict(self.fernet, enc_data_str, ttl, current_time).unwrap()
        return decrypted_dict
  

#
# low-level functions
#
@FernetResult[_Fernet, str]
def fernet_key_generate() -> _Fernet:
    '''
    Generate fernet key
    '''
    _fernet = _Fernet(_Fernet.generate_key())
    return _fernet


@FernetResult[_Fernet, str]
def fernet_key_from_or_generate_file(path: str='fernet.key') -> _Fernet:
    '''
    Load fernet key from file, if key not exists, generate key and write it to the file and return fernet key
    '''
    fernet: _Fernet = None
    
    if os.path.exists(path):
        with open(path, 'rb') as f:
            enc_fernet_key = pickle.load(f)

        # TODO: check use of variable fernet key
        # fernet_key = base64.urlsafe_b64decode(enc_fernet_key)
        fernet = _Fernet(enc_fernet_key) 
    else:
        enc_fernet_key = _Fernet.generate_key()
        # fernet_key = base64.urlsafe_b64decode(enc_fernet_key)
        fernet = _Fernet(enc_fernet_key)

        with open(path, 'wb') as f:
            pickle.dump(enc_fernet_key, f)
      
    return fernet   


@FernetResult[bytes, str]
def fernet_key_encrypt_bytes(fernet: _Fernet, data_bytes: bytes, current_time: int | None=None) -> bytes:
    '''
    Encrypt bytes with fernet key
    '''
    enc_data_bytes: bytes

    if current_time is not None:
        enc_data_bytes = fernet.encrypt_at_time(data_bytes, current_time)
    else:
        enc_data_bytes = fernet.encrypt(data_bytes)

    return enc_data_bytes
 

@FernetResult[bytes, str]
def fernet_key_decrypt_bytes(fernet: _Fernet, enc_data_bytes: bytes, ttl: int | None=None, current_time: int | None=None) -> bytes:
    '''
    Decrypt bytes with fernet key
    '''
    data_bytes: bytes

    if ttl is not None and current_time is not None:
        data_bytes = fernet.decrypt_at_time(enc_data_bytes, ttl, current_time)
    elif ttl is not None and current_time is None:
        data_bytes = fernet.decrypt(enc_data_bytes, ttl)
    else:
        data_bytes = fernet.decrypt(enc_data_bytes)

    return data_bytes
        

@FernetResult[str, str]
def fernet_key_encrypt_dict(fernet: _Fernet, data_dict: dict, current_time: int | None=None) -> str:
    '''
    Encrypt dict with fernet key
    '''
    data_str: str = json.dumps(data_dict)
    data_bytes: bytes = data_str.encode()
    
    # enc_data_bytes: bytes = fernet.encrypt(data_bytes)
    enc_data_bytes: bytes

    if current_time is not None:
        enc_data_bytes = fernet.encrypt_at_time(data_bytes, current_time)
    else:
        enc_data_bytes = fernet.encrypt(data_bytes)

    enc_data_str: str = enc_data_bytes.decode()
    return enc_data_str


@FernetResult[dict, str]
def fernet_key_decrypt_dict(fernet: _Fernet, enc_data_str: str, ttl: int | None=None, current_time: int | None=None) -> dict:
    '''
    Decrypt dict with fernet key
    '''
    enc_data_bytes: bytes = enc_data_str.encode()
    
    # data_bytes: bytes = fernet.decrypt(enc_data_bytes)
    data_bytes: bytes

    if ttl is not None and current_time is not None:
        data_bytes = fernet.decrypt_at_time(enc_data_bytes, ttl, current_time)
    elif ttl is not None and current_time is None:
        data_bytes = fernet.decrypt(enc_data_bytes, ttl)
    else:
        data_bytes = fernet.decrypt(enc_data_bytes)

    data_str: str = data_bytes.decode()
    data_dict: dict = json.loads(data_str)
    return data_dict
