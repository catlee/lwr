#!/usr/bin/env python
import struct
import zlib
import logging
log = logging.getLogger(__name__)
class MessageHandler(object):
    """
    Message format
    0
    <encoder type byte>
    <compressor type byte>
    <data>
    """
    version = 0

    encoders = {}
    compressors = {}

    encoders_by_number = {}
    compressors_by_number = {}

    def __init__(self):
        self.encoder = self.encoders_by_number[max(self.encoders_by_number.keys())]
        self.compressor = self.compressors_by_number[max(self.compressors_by_number.keys())]

    @classmethod
    def register_encoder(cls, e):
        assert e.name not in cls.encoders
        assert e.number not in cls.encoders_by_number
        i = e()
        cls.encoders[e.name] = i
        cls.encoders_by_number[e.number] = i
        return e

    @classmethod
    def register_compressor(cls, c):
        assert c.name not in cls.compressors
        assert c.number not in cls.compressors_by_number
        i = c()
        cls.compressors[c.name] = i
        cls.compressors_by_number[c.number] = i
        return c

    def setEncoder(self, encoder):
        self.encoder = self.encoders[encoder]

    def setCompressor(self, compressor):
        self.compressor = self.compressors[compressor]

    def choose_best(self, encoders, compressors):
        best_encoder = 0
        for e in encoders:
            if e in self.encoders_by_number:
                best_encoder = max(e, best_encoder)

        if best_encoder != self.encoder.number:
            self.encoder = self.encoders_by_number[best_encoder]
            log.debug("Using new encoder %s", self.encoder.name)

        best_compressor = 0
        for c in compressors:
            if c in self.compressors_by_number:
                best_compressor = max(c, best_compressor)

        if best_compressor != self.compressor.number:
            self.compressor = self.compressors_by_number[best_compressor]
            log.debug("Using new compressor %s", self.compressor.name)

    def serialize(self, obj):
        e = self.encoder
        c = self.compressor
        msg = e.encode(obj)
        msg = c.compress(msg)
        return struct.pack("BBB", self.version, e.number, c.number) + msg

    def unserialize(self, msg):
        version = msg[:1]
        if version == b"\x00":
            enum, cnum = struct.unpack("BB", msg[1:3])
            try:
                e = self.encoders_by_number[enum]
            except KeyError:
                raise ValueError("Unsupported encoder %s" % enum)

            try:
                c = self.compressors_by_number[cnum]
            except KeyError:
                raise ValueError("Unsupported compressor %s" % cnum)

            msg = c.decompress(msg[3:])
            return e.decode(msg)
        else:
            raise ValueError("Unsupported version: %s" % version)

@MessageHandler.register_encoder
class RawEncoder(object):
    "Raw encoder"
    number = 0
    name = 'raw'
    def encode(self, obj):
        if not isinstance(obj, (str, bytes)):
            raise ValueError("raw encoder can only handle strings and bytes")
        return obj

    def decode(self, msg):
        return msg

try:
    import simplejson as json
except ImportError:
    import json

@MessageHandler.register_encoder
class JSONEncoder(object):
    "JSON encoder"
    number = 1
    name = 'json'
    def encode(self, obj):
        return json.dumps(obj, separators=",:").encode("utf8")

    def decode(self, msg):
        return json.loads(msg.decode("utf8"))

try:
    import msgpack
    @MessageHandler.register_encoder
    class MsgPackEncoder(object):
        number = 2
        name = 'msgpack'
        def encode(self, obj):
            return msgpack.packb(obj)

        def decode(self, msg):
            return msgpack.unpackb(msg)
except ImportError:
    pass

@MessageHandler.register_compressor
class RawCompressor(object):
    number = 0
    name = 'raw'
    def compress(self, msg):
        return msg

    def decompress(self, msg):
        return msg

@MessageHandler.register_compressor
class ZlibCompressor(object):
    number = 1
    name = 'zlib'
    def compress(self, msg):
        return zlib.compress(msg)

    def decompress(self, msg):
        return zlib.decompress(msg)
