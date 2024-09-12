__all__ = ['BcryptResult', 'Bcrypt']

import os
import pickle

from typing import TypeAlias
import bcrypt as _bcrypt

from thresult.result import Ok, Err


Bcrypt: TypeAlias = 'Bcrypt'
BcryptResult: type = Ok[bytes | bool] | Err[str]


class Bcrypt():
    salt: bytes | None

    def __init__(self, salt: bytes | None=None):
        self.salt = salt


    @classmethod
    @BcryptResult[Bcrypt, str]
    def generate(cls, rounds: int=12, prefix: bytes=b'2b') -> Bcrypt:
        '''
        Generate Bcrypt
        '''
        salt: bytes = bcrypt_salt_generate(rounds, prefix).unwrap()
        self: Bcrypt = Bcrypt(salt)
        return self


    @classmethod
    @BcryptResult[Bcrypt, str]
    def load_or_generate_file(cls, path: str='bcrypt.salt', rounds: int=12, prefix: bytes=b'2b') -> Bcrypt:
        '''
        Load Bcrypt from file, if file not exists, create new Bcrypt, write it to the file, and returns it
        '''
        salt: bytes = bcrypt_salt_from_or_generate_file(path, rounds, prefix).unwrap()
        self: Bcrypt = Bcrypt(salt)
        return self


    @BcryptResult[bytes, str]
    def get_hashed_password(self, unhashed_password: bytes | str) -> bytes:
        '''
        Hashes password with Bcrypt salt
        '''
        return bcrypt_salt_get_hashed_password(self.salt, unhashed_password).unwrap()


    hash_password = get_hashed_password
    hash = get_hashed_password


    @classmethod
    @BcryptResult[bool, str]
    def check_password(cls, unhashed_password: bytes | str, hashed_password: bytes | str) -> bool:
        '''
        Check if plain text password matches with hashed password
        '''
        check_result: bool = bcrypt_salt_check_password(unhashed_password, hashed_password).unwrap()
        return check_result


    check = check_password


#
# low-level functions
#
@BcryptResult[bytes, str]
def bcrypt_salt_generate(rounds: int=12, prefix: bytes=b'2b') -> bytes:
    '''
    Generate bcrypt salt key
    '''
    salt_key: bytes = _bcrypt.gensalt(rounds, prefix)
    return salt_key


@BcryptResult[bytes, str]
def bcrypt_salt_from_or_generate_file(path: str='bcrypt.salt', rounds: int=12, prefix: bytes=b'2b') -> bytes:
    '''
    Load Bcrypt from file, if file not exists, create new Bcrypt, write it to the file, and returns it
    '''
    if os.path.exists(path):
        with open(path, 'rb') as f:
            salt_key = pickle.load(f)
    else:
        salt_key = _bcrypt.gensalt(rounds, prefix)
        
        with open(path, 'wb') as f:
            pickle.dump(salt_key, f)

    return salt_key


@BcryptResult[bytes, str]
def bcrypt_salt_get_hashed_password(salt_key: bytes | str, plain_text_password: bytes | str) -> bytes:
    '''
    Hash password using Bcrypt salt key
    '''
    if isinstance(salt_key, str):
        salt_key = salt_key.encode()  # pragma: no cover

    if isinstance(plain_text_password, str):
        plain_text_password = plain_text_password.encode()

    if len(plain_text_password) > 72:
        raise ValueError(
            'The maximum input length is 72 bytes '
            '(note that UTF8 encoded characters use up to 4 bytes) '
            'and the length of generated hashes is 60 characters.'
        )

    hashpwd = _bcrypt.hashpw(plain_text_password, salt_key)
    return hashpwd


@BcryptResult[bool, str]
def bcrypt_salt_check_password(plain_text_password: bytes | str, hashed_password: bytes | str) -> bool:
    '''
    Check if plain text password matches with hashed password
    '''
    if isinstance(plain_text_password, str):
        plain_text_password = plain_text_password.encode()

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()

    salt_check_pass =_bcrypt.checkpw(plain_text_password, hashed_password)
    return salt_check_pass
