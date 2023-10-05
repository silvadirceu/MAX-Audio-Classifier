import numpy as np
from .bmsgpack import obj_to_msgpack, msgpack_to_obj


def ndarray_to_bytes (array: np.ndarray) -> bytes:
    return obj_to_msgpack(array)


def bytes_to_ndarray (byte_array: bytes) -> np.ndarray:
    obj = msgpack_to_obj(byte_array)
    if type(obj) == np.ndarray:
        obj = obj.copy()
    return obj