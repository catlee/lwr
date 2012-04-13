import unittest
from nose import SkipTest

import lwr.plugins.zmq.message as message

class TestEncoders(unittest.TestCase):
    def setUp(self):
        self.message = {"msg": "hello", "bool": True, "null": None, "list": [1,2,3,4], "tuple": (1,2,3), "dict": {"1":2}}

    def test_json_encoder(self):
        e = message.JSONEncoder()
        encoded = e.encode(self.message)
        decoded = e.decode(encoded)

        # JSON doesn't distinguish between tuples and lists, so we expect
        # "tuple" here to be changed into a list
        decoded['tuple'] = tuple(decoded['tuple'])
        self.assertEquals(self.message, decoded)

    def test_raw_encoder(self):
        e = message.RawEncoder()
        msg = "hello world"
        encoded = e.encode(msg)
        decoded = e.decode(encoded)

        self.assertEquals(msg, decoded)

        # Raw encoder can't handle objects
        with self.assertRaises(ValueError):
            e.encode(self.message)

    def test_msgpack_encoder(self):
        if 'msgpack' not in message.MessageHandler.encoders:
            raise SkipTest

        e = message.MsgPackEncoder()
        encoded = e.encode(self.message)
        decoded = e.decode(encoded)

        # msgpack doesn't distinguish between tuples and lists, so we expect
        # "list" here to be changed into a tuple
        decoded['list'] = list(decoded['list'])
        self.assertEquals(self.message, decoded)

class TestCompressors(unittest.TestCase):
    def setUp(self):
        self.message = message.json.dumps({"msg": "hello", "bool": True, "null": None, "list": [1,2,3,4], "tuple": (1,2,3), "dict": {"1":2}}).encode("utf8")

    def test_raw_compressor(self):
        c = message.RawCompressor()
        compressed = c.compress(self.message)
        decompressed = c.decompress(compressed)

        self.assertEquals(self.message, decompressed)
        self.assertEquals(self.message, compressed)

    def test_zlib_compressor(self):
        c = message.ZlibCompressor()
        compressed = c.compress(self.message)
        decompressed = c.decompress(compressed)

        self.assertEquals(self.message, decompressed)

class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.message = {"msg": "hello", "bool": True, "null": None, "list": [1,2,3,4], "tuple": (1,2,3), "dict": {"1":2}}

    def test_serialize(self):
        mh = message.MessageHandler()
        mh.setEncoder('json')
        mh.setCompressor('raw')
        s = mh.serialize(self.message)
        self.assertEquals(s[:1], b"\x00", s)

        m = mh.unserialize(s)
        # JSON doesn't distinguish between tuples and lists, so we expect
        # "tuple" here to be changed into a list
        m['tuple'] = tuple(m['tuple'])
        self.assertEquals(m, self.message)

    def test_choose_best(self):
        mh = message.MessageHandler()

        mh.choose_best(encoders=[0], compressors=[0])
        self.assertEquals(mh.encoder.name, 'raw')
        self.assertEquals(mh.compressor.name, 'raw')

        mh.choose_best(encoders=[0,1], compressors=[0])
        self.assertEquals(mh.encoder.name, 'json')
        self.assertEquals(mh.compressor.name, 'raw')

        mh.choose_best(encoders=[0,1], compressors=[0,1])
        self.assertEquals(mh.encoder.name, 'json')
        self.assertEquals(mh.compressor.name, 'zlib')

        mh.choose_best(encoders=[0,1,1000], compressors=[0,1,1000])
        self.assertEquals(mh.encoder.name, 'json')
        self.assertEquals(mh.compressor.name, 'zlib')

    def test_invalid_msg(self):
        mh = message.MessageHandler()

        with self.assertRaises(ValueError):
            mh.unserialize(b"\xff\xff\xff")

        with self.assertRaises(ValueError):
            mh.unserialize(b"\x00\xff\xff")

        with self.assertRaises(ValueError):
            mh.unserialize(b"\x00\x00\xff")

        self.assertEquals(b"", mh.unserialize(b"\x00\x00\x00"))
