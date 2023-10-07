import msgpack
import msgpack_numpy as m

m.patch()


def obj_to_msgpack(obj):
    return msgpack.packb(obj)


def msgpack_to_obj(bytes):
    return msgpack.unpackb(bytes)
