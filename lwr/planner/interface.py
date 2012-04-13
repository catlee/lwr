class PlannerStore(object):
    """
    Base class for planner storage.

    Specific implementations should inherit from this, or at least implement all the same methods.
    """
    def getPlan(self, _id):
        """
        Returns a Plan object with the given id.
        Raises KeyError if it's not found.
        """
        raise NotImplementedError

    def findPlansByBucket(self, bucket):
        """
        Returns a list of Plan objects in the given bucket.
        """
        raise NotImplementedError

    def findPlansByEventType(self, event_type, bucket=None):
        """
        Returns a list of Plan objects subscribed to `event_type`.
        If bucket is given, restrict results to Plans within the given bucket.
        """
        raise NotImplementedError

    def addPlan(self, p):
        """
        Adds a Plan to the store.
        TODO: generate id here?
        """
        raise NotImplementedError

    def updatePlan(self, p):
        """
        Updates Plan. Requires that p.id is set
        """
        raise NotImplementedError

class EventReceiver(object):
    def __init__(self, store=None):
        """
        If store is set it should be an EventStore object where we'll save
        events as they arrive
        """
        raise NotImplementedError

    def listen(self, endpoint):
        """
        Listen to endpoint for new events
        """
        raise NotImplementedError

    def getEvent(self, timeout=None):
        """
        Get the next event. Wait for timeout milli-seconds or forever if timeout is
        None
        """
        raise NotImplementedError

class EventPublisher(object):
    def addSocket(self, endpoint):
        """
        Add endpoint to list of places we publish to
        """
        raise NotImplementedError

    def sendEvent(self, e):
        """
        Send event e to all our endpoints
        """
        raise NotImplementedError
