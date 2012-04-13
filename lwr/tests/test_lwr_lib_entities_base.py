import unittest
import mock
from lwr.lib.entities.base import Entity, VersionedEntity, UnsupportedVersion, LoggedEntityMixin

class TestEntity(unittest.TestCase):
    def test_entity_slots(self):
        # test that base entities are using slots correctly
        e = Entity()
        self.assertFalse(hasattr(e, '__dict__'))
        self.assertTrue(hasattr(e, '__slots__'))

    def test_nonslots_subclass(self):
        # test our understanding of how __slots__ works with subclassing.  a
        # subclass that doesn't declare __slots__ should create objects with a
        # __dict__ 
        class T(Entity):
            pass

        t = T(x=1)
        # Check that we have a __dict__ attribute
        self.assertTrue(hasattr(t, '__dict__'))

    def test_simple_entity(self):
        class T(Entity):
            __slots__ = ('x',)

        t = T(x=1)

        # Check that we still have slots
        self.assertFalse(hasattr(t, '__dict__'))
        self.assertTrue(hasattr(t, '__slots__'))

        # Check that asDict works
        self.assertEquals(t.asDict(), {'x': 1})

        # Check that fromDict works
        t1 = T.fromDict({'x': 1})
        self.assertEquals(t1.x, 1)

        # Check that creating an object without specifying values raises an error
        with self.assertRaises(KeyError):
            t = T()

    def test_entity_defaults(self):
        class T(Entity):
            __slots__ = ('x','y')
            __defaults__ = {'x':[1]}

        t = T(y=2)
        self.assertEquals(t.x, [1])
        self.assertEquals(t.y, 2)

        # Check that defaults get copied properly
        t.x.append(2)
        t1 = T(y=2)
        self.assertEquals(t.x, [1,2])
        self.assertEquals(t1.x, [1])

        with self.assertRaises(KeyError):
            t = T(x=3)

    def test_entity_nested_types(self):
        class T(Entity):
            __slots__ = ('x',)

        class U(Entity):
            __slots__ = ('t',)
            __nested_types__ = {'t': T}

        t = T(x=1)
        u = U(t=t)

        d = u.asDict()
        self.assertEquals(d, {'t': {'x': 1}})

        u1 = U.fromDict(d)
        self.assertIsInstance(u1.t, T)

    def test_entity_copy(self):
        class T(Entity):
            __slots__ = ('x',)

        t = T(x=[1,2,3])
        t1 = t.copy()

        self.assertEquals(t.x, t1.x)
        self.assertIsNot(t.x, t1.x)

class TestVersionedEntity(unittest.TestCase):
    def test_simple_versionedentity(self):
        class T(VersionedEntity):
            v=1
            __slots__ = ('x',)

        t = T(x=5)
        self.assertEquals(t.v, 1)
        self.assertEquals(t.x, 5)

        # Check that we still have slots
        self.assertFalse(hasattr(t, '__dict__'))
        self.assertTrue(hasattr(t, '__slots__'))

    def test_fromdict(self):
        class T(VersionedEntity):
            v=1
            __slots__ = ('x',)

        t = T.fromDict({'x': 1, 'v': 1})
        self.assertEquals(t.x, 1)

    def test_unsupported_version(self):
        class T(VersionedEntity):
            v=1
            __slots__ = ('x',)

        with self.assertRaises(UnsupportedVersion):
            T.fromDict({'x': 1, 'v': 2})

    def test_upgrade(self):
        class T(VersionedEntity):
            v=1
            __slots__ = ('x',)

            @classmethod
            def fromOldDict(cls, d):
                if d['v'] == 0:
                    return cls(x=d['x']+1)

        t = T.fromDict({'x': 1, 'v':0})
        self.assertEquals(t.x, 2)

    def test_upgrade_notimplemented(self):
        class T(VersionedEntity):
            v=1
            __slots__ = ('x',)

        with self.assertRaises(NotImplementedError):
            T.fromDict({'x': 1, 'v':0})

class TestLoggedEntityMixin(unittest.TestCase):
    def test_log(self):
        class T(VersionedEntity, LoggedEntityMixin):
            v = 1
            __slots__ = ('x','log')
            __defaults__ = {'log': []}

        t = T(x=1)
        with mock.patch('time.time') as f:
            f.return_value = 12345
            t.addLog("Hi")
            t.addLog("There", t=123456)

        self.assertEquals(t.log, [(12345, "Hi"), (123456, "There")])
