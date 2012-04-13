import logging
log = logging.getLogger(__name__)

class Planner(object):
    planner_store = None
    job_publisher = None

    def __init__(self, config):
        self.config = config

        self.event_receivers = []

        self.setupStore()
        self.setupEventReceivers()

    def setupStore(self):
        """
        Instantiate a planner store based on config
        """

    def setupEventListeners(self):
        """
        Set up listeners for events
        """

    def run(self):
        """
        Start running!
        This never returns
        """
        # TODO: Have different implementations that do this better.
        # e.g. one thread or greenlet per receiver
        for l in self.event_receivers:
            e = l.getEvent(100)
            if e:
                self.handleEvent(e)

    def handleEvent(self, e):
        # Find plans subscribed to this event
        plans = self.planner_store.findPlansByEventType("%s.%s" % (e.bucket, e.type))
        jobs = []
        for p in plans:
            j = p.run(e)
            log.debug("Created new job %s", j.asDict())
            jobs.append(j)
            # TODO: Send new job somewhere!
        return jobs
