import time
import copy
from collections import Mapping
class UnsupportedVersion(Exception):
    pass

class Entity(object):
    __slots__ = ()
    __nested_types__ = {}
    __defaults__ = {}

    def __init__(self, **kwargs):
        # The idea here is to go through the __slots__ of all the classes self
        # is inherited from. For each item in __slots__, set our attribute from
        # the corresponding argument in kwargs. If we can't find it in kwargs,
        # then check __defaults__.
        for c in self.__class__.__mro__:
            if c is object:
                continue
            for s in c.__slots__:
                if not hasattr(self, s):
                    if s in kwargs:
                        v = kwargs[s]
                    elif s in self.__defaults__:
                        v = copy.deepcopy(self.__defaults__[s])
                    else:
                        raise KeyError(s)
                    if s in self.__nested_types__ and isinstance(v, Mapping):
                        v = self.__nested_types__[s].fromDict(v)
                    setattr(self, s, v)

    def asDict(self):
        retval = {}
        for c in self.__class__.__mro__:
            if c is object:
                continue
            for s in c.__slots__:
                v = getattr(self, s)
                if hasattr(v, 'asDict'):
                    v = v.asDict()
                retval[s] = v
        return retval

    @classmethod
    def fromDict(cls, d):
        return cls(**d)

    def copy(self):
        return self.__class__.fromDict(copy.deepcopy(self.asDict()))

class VersionedEntity(Entity):
    __slots__ = ('v',)

    @classmethod
    def fromOldDict(cls, d):
        raise NotImplementedError

    @classmethod
    def fromDict(cls, d):
        if cls.v == d['v']:
            # Don't need to pass in version attribute
            d = d.copy()
            del d['v']
            return cls(**d)
        elif cls.v > d['v']:
            # Need to upgrade
            return cls.fromOldDict(d)
        else:
            raise UnsupportedVersion

class LoggedEntityMixin(object):
    __slots__ = ()
    def addLog(self, msg, t=None):
        if t is None:
            t = time.time()
        self.log.append( (t, msg) )
