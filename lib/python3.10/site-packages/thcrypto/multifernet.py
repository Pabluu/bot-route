__all__ = ['MultiFernetResult', 'MultiFernet']

import json

from typing import TypeAlias
from cryptography.fernet import MultiFernet as _MultiFernet
from cryptography.fernet import Fernet as _Fernet

from thresult.result import Ok, Err

from .fernet import Fernet


MultiFernet: TypeAlias = 'MultiFernet'
MultiFernetResult: type = Ok[bytes | str | dict] | Err[str]


class MultiFernet():

    def __init__(self, fernet_keys: list[Fernet]):
        self.fernets: list[Fernet] = fernet_keys

        # visit fernet_keys and get low-level/cryptography Fernet instance
        _fernet_keys: list[_Fernet] = [n.fernet for n in self.fernets]

        # create low-level/cryptography MultiFernet instance
        self._multi_fernet = _MultiFernet(_fernet_keys)


    @MultiFernetResult[bytes, str]
    def encrypt_bytes(self,
                      data_bytes: bytes,
                      current_time: int | None=None) -> bytes:
        '''
        Encrypt bytes with multi-fernet.
        '''
        encrypted_bytes: bytes = multifernet_key_encrypt_bytes(self._multi_fernet,
                                                               data_bytes,
                                                               current_time).unwrap()
        return encrypted_bytes


    @MultiFernetResult[bytes, str]
    def decrypt_bytes(self,
                      enc_data_bytes: bytes,
                      ttl: int | None=None,
                      current_time: int | None=None) -> bytes:
        '''
        Decrypt bytes with multi-fernet.
        '''
        decrypted_bytes: bytes = multifernet_key_decrypt_bytes(self._multi_fernet,
                                                               enc_data_bytes, ttl,
                                                               current_time).unwrap()
        return decrypted_bytes


    @MultiFernetResult[str, str]
    def encrypt_dict(self,
                     data_dict: dict,
                     current_time: int | None=None) -> str:
        '''
        Encrypt dict with multi-fernet.
        '''
        encrypted_dict: str = multifernet_key_encrypt_dict(self._multi_fernet,
                                                           data_dict,
                                                           current_time).unwrap()
        return encrypted_dict


    @MultiFernetResult[dict, str]
    def decrypt_dict(self,
                     enc_data_str: str,
                     ttl: int | None=None,
                     current_time: int | None=None) -> dict:
        '''
        Decrypt dict with multi-fernet.
        '''
        decrypted_dict: dict = multifernet_key_decrypt_dict(self._multi_fernet,
                                                            enc_data_str, ttl,
                                                            current_time).unwrap()
        return decrypted_dict


    @MultiFernetResult[MultiFernet, str]
    def add_fernet(self, fernet: Fernet) -> MultiFernet:
        '''
        Add new Fernet key
        '''

        # add new Fernet at beginning of list
        updated_fernet_list: list[Fernet] = [fernet, *self.fernets]

        # create and return new MultiFernet instance
        return MultiFernet(updated_fernet_list)


    @MultiFernetResult[bytes, str]
    def rotate(self, enc_data_bytes: bytes) -> bytes:
        '''
        Rotate Fernet keys
        '''
        decrypted_bytes: bytes = multifernet_key_rotate_bytes(self._multi_fernet,
                                                              enc_data_bytes).unwrap()
        return decrypted_bytes


#
# low-level functions
#
@MultiFernetResult[bytes, str]
def multifernet_key_encrypt_bytes(multifernet: _MultiFernet,
                                  data_bytes: bytes,
                                  current_time: int | None=None) -> bytes:
    '''
    Encrypt bytes with multifernet key
    '''
    enc_data_bytes: bytes

    if current_time is not None:
        enc_data_bytes = multifernet.encrypt_at_time(data_bytes, current_time)
    else:
        enc_data_bytes = multifernet.encrypt(data_bytes)

    return enc_data_bytes


@MultiFernetResult[bytes, str]
def multifernet_key_decrypt_bytes(multifernet: _MultiFernet,
                                  enc_data_bytes: bytes,
                                  ttl: int | None=None,
                                  current_time: int | None=None) -> bytes:
    '''
    Decrypt bytes with multifernet key
    '''
    data_bytes: bytes

    if ttl is not None and current_time is not None:
        data_bytes = multifernet.decrypt_at_time(enc_data_bytes, ttl, current_time)
    elif ttl is not None and current_time is None:
        data_bytes = multifernet.decrypt(enc_data_bytes, ttl)
    else:
        data_bytes = multifernet.decrypt(enc_data_bytes)

    return data_bytes


@MultiFernetResult[str, str]
def multifernet_key_encrypt_dict(multifernet: _MultiFernet,
                                 data_dict: dict,
                                 current_time: int | None=None) -> str:
    '''
    Encrypt dict with multifernet key
    '''
    data_str: str = json.dumps(data_dict)
    data_bytes: bytes = data_str.encode()
    enc_data_bytes: bytes

    if current_time is not None:
        enc_data_bytes = multifernet.encrypt_at_time(data_bytes, current_time)
    else:
        enc_data_bytes = multifernet.encrypt(data_bytes)

    enc_data_str: str = enc_data_bytes.decode()
    return enc_data_str


@MultiFernetResult[dict, str]
def multifernet_key_decrypt_dict(multifernet: _MultiFernet,
                                 enc_data_str: str,
                                 ttl: int | None=None,
                                 current_time: int | None=None) -> dict:
    '''
    Decrypt dict with multifernet key
    '''
    enc_data_bytes: bytes = enc_data_str.encode()
    data_bytes: bytes

    if ttl is not None and current_time is not None:
        data_bytes = multifernet.decrypt_at_time(enc_data_bytes, ttl, current_time)
    elif ttl is not None and current_time is None:
        data_bytes = multifernet.decrypt(enc_data_bytes, ttl)
    else:
        data_bytes = multifernet.decrypt(enc_data_bytes)

    data_str: str = data_bytes.decode()
    data_dict: dict = json.loads(data_str)
    return data_dict


@MultiFernetResult[bytes, str]
def multifernet_key_rotate_bytes(multifernet: _MultiFernet,
                                 enc_data_bytes: bytes) -> bytes:
    '''
    Decrypt bytes with multi multifernet key with key rotation
    '''
    data_bytes: bytes = multifernet.rotate(enc_data_bytes)
    return data_bytes
