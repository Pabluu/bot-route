__all__ = [
    'gen_random_int',
    'gen_random_int_hex',
    'gen_random_int_hex_bytes',
    'gen_random_int128',
    'gen_random_int128_hex',
    'gen_random_int128_hex_bytes',
    'gen_random_int256',
    'gen_random_int256_hex',
    'gen_random_int256_hex_bytes',
]

import os

from thresult import Ok, Err


RandResult: type = Ok[int | str | bytes] | Err[str]


@RandResult[int, str]
def gen_random_int(bits: int) -> int:
    '''
    Generate a random integer
    '''
    assert isinstance(bits, int)
    # min_v: int = 0
    # max_v: int = 2 ** bits

    bits = bits
    n_bytes = bits // 8
    v = int.from_bytes(os.urandom(n_bytes), byteorder='big')
    return v


@RandResult[str, str]
def gen_random_int_hex(bits: int) -> str:
    '''
    Generate random string based on hexadecimal representation of an random integer
    '''
    r: int = gen_random_int(bits).unwrap()
    h: str = hex(r)
    v: str = h[2:]
    return v


@RandResult[bytes, str]
def gen_random_int_hex_bytes(bits: int) -> bytes:
    '''
    Generate random bytes
    '''
    s: str = gen_random_int_hex(bits).unwrap()
    v: bytes = s.encode()
    return v


@RandResult[int, str]
def gen_random_int128() -> int:
    '''
    Generate a random integer
    '''
    return gen_random_int(128).unwrap()


@RandResult[str, str]
def gen_random_int128_hex() -> str:
    '''
    Generate random string based on hexadecimal representation of an random integer
    '''
    return gen_random_int_hex(128).unwrap()


@RandResult[bytes, str]
def gen_random_int128_hex_bytes() -> bytes:
    '''
    Generate random bytes
    '''
    return gen_random_int_hex_bytes(128).unwrap()


@RandResult[int, str]
def gen_random_int256() -> int:
    '''
    Generate a random integer
    '''
    return gen_random_int(256).unwrap()


@RandResult[str, str]
def gen_random_int256_hex() -> str:
    '''
    Generate random string based on hexadecimal representation of an random integer
    '''
    return gen_random_int_hex(256).unwrap()


@RandResult[bytes, str]
def gen_random_int256_hex_bytes() -> bytes:
    '''
    Generate random bytes
    '''
    return gen_random_int_hex_bytes(256).unwrap()
