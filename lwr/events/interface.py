class EventStore(object):
    """
    Base class for event storage.

    Specific implementations should inherit from this, or at least implement all the same methods.
    """
    def setMaxSize(self, m):
        """
        Set the maximum number of events to keep.
        Set to None to keep all events.
        """
        raise NotImplementedError

    def getEvent(self, _id):
        """
        Returns a Event object with the given id.
        Raises KeyError if it's not found.
        """
        raise NotImplementedError

    def findEventsByBucket(self, bucket):
        """
        Returns a list of event objects in the given bucket.
        """
        raise NotImplementedError

    def findEventsByType(self, event_type, bucket=None):
        """
        Returns a list of event objects of the given type. If bucket is
        specified, search the given bucket.
        """
        raise NotImplementedError

    def addEvent(self, e):
        """
        Adds a Event to the store.
        TODO: generate id here?
        """
        raise NotImplementedError
