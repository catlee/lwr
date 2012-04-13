from lwr.lib.entities.base import VersionedEntity, LoggedEntityMixin

class Event(VersionedEntity, LoggedEntityMixin):
    v = 0
    __slots__ = ('owner', 'bucket', 'type', 'data', 'log', 'sigs')
    __defaults__ = {
            'data': None,
            'log': [],
            'sigs': None,
            }
