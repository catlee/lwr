from lwr.planner.interface import PlannerStore
from lwr.events.interface import EventStore

class DummyPlannerStore(PlannerStore):
    def __init__(self, config):
        self.config = config

class DummyEventStore(EventStore):
    def __init__(self, config):
        self.config = config
