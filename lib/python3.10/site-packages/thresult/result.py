__all__ = [
    'ResultException', 'ResultType', 'WrappedBase', 'UnwrappedBase',
    'Result', 'Ok', 'Err', 'unwrap',
    'wrap_result', 'auto_unwrap',
]

import asyncio
import inspect
import builtins
import threading
from functools import wraps
from contextlib import contextmanager
from types import UnionType, GenericAlias, new_class
from typing import Any, Callable, ForwardRef


# per-thread Result objects of each Result decorated function call
_Thread_Err_map = {}


class ResultException(Exception):
    pass


class _ResultType(type):
    pass


class ResultType(_ResultType):
    def __getitem__(cls, key: Any) -> type:
        V: type
        E: type

        if cls is Ok or issubclass(cls, Ok):
            V = key

            if not (isinstance(V, (type, ForwardRef, str, UnionType, GenericAlias)) or V in (Any,)):
                raise TypeError(f'Type {V} sould be instance of type')

            T: ResultType = type(
                f'Ok[{key}]',
                (Ok,),
                {'__annotations__': {'v': V}}
            )
        elif cls is Err or issubclass(cls, Err):
            E = key

            if not (isinstance(E, (type, ForwardRef, str, UnionType, GenericAlias)) or E in (Any,)):
                raise TypeError(f'Type {E} sould be instance of type')

            T: ResultType = type(
                f'Err[{key}]',
                (Err,),
                {'__annotations__': {'e': E}}
            )
        elif cls is Result or issubclass(cls, Result):
            if isinstance(key, (tuple, list)):
                if len(key) == 1:
                    V = key[0]
                    E = Exception
                elif len(key) == 2:
                    V, E = key
                else:
                    raise TypeError(f'Type {key} sould be instance of type or tuple[type, type]')
            elif isinstance(key, (type, ForwardRef, str, UnionType, GenericAlias)) or key in (Any,):
                V = key
                E = Exception
            else:
                raise TypeError(f'Type {key} sould be instance of type or tuple[type, type]')

            if not (isinstance(V, (type, ForwardRef, str, UnionType, GenericAlias)) or V in (Any,)):
                raise TypeError(f'Type {V} sould be instance of type')

            if not (isinstance(E, (type, ForwardRef, str, UnionType, GenericAlias)) or E in (Any,)):
                raise TypeError(f'Type {E} sould be instance of type')

            T: ResultType = type(
                f'Result[{key}]',
                (Result,),
                {'__annotations__': {'v': V, 'e': E}}
            )
        else:
            raise TypeError(f'Unsupported type {cls}') # pragma: no cover

        return T


    def __or__(cls: type, other: type) -> 'ResultType':
        V: type = cls.__annotations__['v']
        E: type = other.__annotations__['e']

        if not (isinstance(V, (type, ForwardRef, str, UnionType, GenericAlias)) or V in (Any,)):
            raise TypeError(f'Type {V} sould be instance of type')

        if not (isinstance(E, (type, ForwardRef, str, UnionType, GenericAlias)) or E in (Any,)):
            raise TypeError(f'Type {E} sould be instance of type')

        T: ResultType = type(
            f'Result[{V}, {E}]',
            (Result,),
            {'__annotations__': {'v': V, 'e': E}}
        )

        return T


    def __eq__(cls: type, other: type) -> bool:
        return (
            cls.__annotations__['v'] == other.__annotations__['v'] and
            cls.__annotations__['e'] == other.__annotations__['e']
        )


    def __call__(cls, *args, **kwargs) -> Callable:
        if (
            len(args) == 1 and
            not kwargs and
            not issubclass(cls, Ok) and
            not issubclass(cls, Err) and
            (fn := args[0]) and
            (callable(fn) or asyncio.iscoroutinefunction(fn))
        ):
            V: type = cls.__annotations__.get('v', fn.__annotations__.get('return', Any))
            E: type = cls.__annotations__.get('e', Exception)

            if not (isinstance(V, (type, ForwardRef, str, UnionType, GenericAlias)) or V in (Any,)):
                raise TypeError(f'Type {V} sould be instance of type')

            if not (isinstance(E, (type, ForwardRef, str, UnionType, GenericAlias)) or E in (Any,)):
                raise TypeError(f'Type {E} sould be instance of type')
            
            if asyncio.iscoroutinefunction(fn):
                @wraps(fn)
                async def wrap(*args, **kwargs) -> cls:
                    global _Thread_Err_map
                    r: Result

                    try:
                        v = await fn(*args, **kwargs)
                        r = Ok[V](v)
                    except Exception as e:
                        r = Err[E](e)
                    
                    t = threading.current_thread()

                    if t in _Thread_Err_map:
                        _Thread_Err_map[t] = r
                        r = r.unwrap()

                    return r
            elif inspect.isfunction(fn) or inspect.ismethod(fn):
                @wraps(fn)
                def wrap(*args, **kwargs) -> cls:
                    global _Thread_Err_map
                    r: Result

                    try:
                        v = fn(*args, **kwargs)
                        r = Ok[V](v)
                    except Exception as e:
                        r = Err[E](e)
                    
                    t = threading.current_thread()
                    
                    if t in _Thread_Err_map:
                        _Thread_Err_map[t] = r
                        r = r.unwrap()

                    return r
            elif callable(fn):
                def wrap(*args, **kwargs) -> cls:
                    global _Thread_Err_map
                    r: Result

                    try:
                        v = fn(*args, **kwargs)
                        r = Ok[V](v)
                    except Exception as e:
                        r = Err[E](e)
                    
                    t = threading.current_thread()
                    
                    if t in _Thread_Err_map:
                        _Thread_Err_map[t] = r
                        r = r.unwrap()

                    return r
            else:
                raise TypeError(f'Unsupported type of fn {fn}') # pragma: no cover

            return wrap
        else:
            return super().__call__(*args, **kwargs)


class _Result(metaclass=ResultType):
    v: type | None = None
    e: type | None = None


class Result(_Result):
    def __new__(cls, *args, **kwargs) -> None:
        raise TypeError('Cannot be instantiated')


    def __enter__(self):
        try:
            v = self.unwrap()
        except Exception as e:
            self.__exit__(type(e), e, e.__traceback__)

        return v


    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type or exc_value:
            raise exc_value

        return self


class Ok(Result):
    __match_args__ = ('v',)
    v: Any


    def __new__(cls, *args, **kwargs) -> 'Ok':
        self = _Result.__new__(cls)
        return self


    def __init__(self, v: Any):
        V: type = self.__class__.__annotations__['v']

        if not (isinstance(V, GenericAlias) or
                isinstance(V, UnionType) or
                isinstance(V, str) or
                V is Any or
                isinstance(V, ForwardRef) or
                isinstance(v, V)):
            raise TypeError(f'Got {type(v)} but expected {self.__class__.__annotations__["v"]}')
        
        self.v = v


    def unwrap(self) -> Any:
        """
        This function unwrap and returns a value of Ok type of Result
        """
        return self.v


    def unwrap_or(self, v: Any) -> Any:
        """
        This function unwrap and returns a value of Ok type of Result
        """
        return self.v


    def unwrap_value(self) -> Any:
        """
        This function unwrap and returns a value of Ok type of Result
        """
        return self.v


class Err(Result):
    __match_args__ = ('e',)
    e: Any


    def __new__(cls, *args, **kwargs) -> 'Err':
        self = _Result.__new__(cls)
        return self


    def __init__(self, e: Any):
        E: type = self.__class__.__annotations__['e']

        if not (isinstance(E, GenericAlias) or
                isinstance(E, UnionType) or
                isinstance(E, str) or
                E is Any or
                isinstance(E, ForwardRef) or
                isinstance(e, (E, Exception))):
            raise TypeError(f'Got {type(e)} but expected {self.__class__.__annotations__["e"]}')

        self.e = e


    def unwrap(self) -> None:
        """
        This function unwrap and raise exception of Error type of Err type of Result
        """
        if not isinstance(self.e, Exception):
            e = ResultException(self.e)
        else:
            e = self.e # pragma: no cover

        raise e


    def unwrap_or(self, v: Any) -> Any:
        """
        This function unwrap and returns a value
        """
        return v


    def unwrap_value(self) -> Any:
        """
        This function unwrap and returns a value of Err type of Result
        """
        return self.e


def wrap_result(res: Result):
    """
    This function wraps the Result type and returns a Ok or Err type of Result
    """
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if asyncio.iscoroutinefunction(f):
                async def a():
                    try:
                        v = await f(*args, **kwargs)
                        return Ok(v)
                    except Exception as e:
                        return Err(e)  
                
                return a()
            else:
                try:
                    v = f(*args, **kwargs)
                    return Ok(v)
                except Exception as e:
                    return Err(e)

        return inner

    return outer


class WrappedBase:
    def __getstate__(self) -> dict:
        state = {}

        for a in dir(self):
            if a.startswith('__') and a.endswith('__'):
                continue

            v = getattr(self, a)

            if callable(v):
                continue

            state[a] = v

        return state


class UnwrappedBase:
    def __setstate__(self, state):
        for a, v in state.items():
            setattr(self, a, v)

#
# unwrap
#
class Unwrap:
    def __enter__(self):
        global _Thread_Err_map
        t = threading.current_thread()
        _Thread_Err_map[t] = None
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        global _Thread_Err_map
        t = threading.current_thread()
        del _Thread_Err_map[t]


unwrap = Unwrap


#
# auto unwrap
#
_old_to_new_type_map = {}


def _has_new_type(old_type):
    global _old_to_new_type_map

    if old_type in _old_to_new_type_map:
        return True

    return False


def _get_new_type(old_type, default=NotImplemented):
    global _old_to_new_type_map

    if old_type in builtins.__dict__.values():
        return old_type

    if old_type in _old_to_new_type_map:
        new_type = _old_to_new_type_map[old_type]
        return new_type

    if default is NotImplemented:
        raise KeyError(f'missing key: {old_type}')

    return default


def _set_new_type(old_type, new_type):
    global _old_to_new_type_map
    _old_to_new_type_map[old_type] = new_type


def _auto_unwrap_type(type_):
    if _has_new_type(type_):
        new_type = _get_new_type(type_)
        return new_type
    
    new_type = new_class(type_.__name__, (type_, UnwrappedBase))
    _set_new_type(type_, new_type)

    for a in dir(type_):
        f = getattr(type_, a)

        if not callable(f):
            continue

        if not hasattr(f, '__annotations__'):
            continue

        return_type = f.__annotations__.get('return')

        if not return_type:
            continue

        if _has_new_type(return_type):
            new_return_type = _get_new_type(return_type)
        else:
            new_return_type = auto_unwrap(return_type)

        new_f = _auto_unwrap_func(f)
        setattr(new_type, a, new_f)
    
    return new_type


def _auto_unwrap_func(func):
    global _old_to_new_type_map
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            async def a():
                r = await func(*args, **kwargs)

                if isinstance(r, Result):
                    r = r.unwrap()

                old_type = type(r)
                new_type = _get_new_type(old_type)
                
                if (inspect.isclass(old_type) and issubclass(old_type, WrappedBase) and isinstance(r, old_type)) or \
                   (isinstance(old_type, ForwardRef) and old_type.__forward_arg__ == r.__class__.__name__):
                    new_r = new_type.__new__(new_type)
                    state = r.__getstate__()
                    new_r.__setstate__(state)
                    r = new_r
                
                return r
            
            return a()
        elif inspect.ismethod(func):
            r = func(*args, **kwargs)

            if isinstance(r, Result):
                r = r.unwrap()

            old_type = type(r)
            new_type = _get_new_type(old_type)
            
            if (inspect.isclass(old_type) and issubclass(old_type, WrappedBase) and isinstance(r, old_type)) or \
               (isinstance(old_type, ForwardRef) and old_type.__forward_arg__ == r.__class__.__name__):
                new_r = new_type.__new__(new_type)
                state = r.__getstate__()
                new_r.__setstate__(state)
                r = new_r

            return r
        else:
            r = func(*args, **kwargs)

            if isinstance(r, Result):
                r = r.unwrap()

            old_type = type(r)
            new_type = _get_new_type(old_type)
            
            if (inspect.isclass(old_type) and issubclass(old_type, WrappedBase) and isinstance(r, old_type)) or \
               (isinstance(old_type, ForwardRef) and old_type.__forward_arg__ == r.__class__.__name__):
                new_r = new_type.__new__(new_type)
                state = r.__getstate__()
                new_r.__setstate__(state)
                r = new_r

            return r

    return wrapper


def auto_unwrap(obj) -> Any:
    '''
    This function auto unwraps Ok or Err type of Result
    '''
    if inspect.isclass(obj):
        if issubclass(obj, WrappedBase):
            r = _auto_unwrap_type(obj)
        else:
            r = obj
    else:
        r = _auto_unwrap_func(obj)
    
    return r


if __name__ == '__main__':
    @Result
    def div(x: float, y: float) -> float:
        # can raise "ZeroDivisionError: division by zero" exception
        z: float = x / y
        return z


    match r := div(1.0, 2.0): # Ok[float](0.5)
        case Ok(v):
            assert v == 0.5
        case Err(e):
            # unreachable
            # "ZeroDivisionError: division by zero"
            assert isinstance(e, ZeroDivisionError)
