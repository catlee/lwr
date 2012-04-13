from lwr.planner.interface import PlannerStore
from lwr.planner.plan import Plan

import pymongo
from bson.objectid import ObjectId

def to_mongo_id(o):
    """
    Converts 'id' to '_id'
    """
    o['_id'] = ObjectId(o['id'])
    del o['id']
    return o

def from_mongo_id(o):
    """
    Converts '_id' to 'id'
    """
    o['id'] = str(o['_id'])
    del o['_id']
    return o

class MongoPlannerStore(PlannerStore):
    def __init__(self, config):
        self.config = config
        self.connection = pymongo.Connection(config['hosts'].split(','))

        self.db = self.connection[config['database']]
        self.col = self.db[config['collection']]
        self.col.ensure_index('bucket')
        self.col.ensure_index('events')

    def getPlan(self, _id):
        p = self.col.find_one({"_id": ObjectId(_id)})
        if not p:
            raise KeyError("Plan %s not found" % _id)

        p = from_mongo_id(p)
        return Plan.fromDict(p)

    def findPlansByBucket(self, bucket):
        retval = []
        plans = self.col.find({"bucket": bucket})
        for p in plans:
            p = from_mongo_id(p)
            p = Plan.fromDict(p)
            retval.append(p)
        return retval

    def addPlan(self, p):
        assert p.id is None
        p_dict = p.asDict()
        _id = str(self.col.insert(p_dict))
        p.id = _id
        return _id

    def updatePlan(self, p):
        p_dict = to_mongo_id(p.asDict())
        self.col.update({"_id": p_dict['_id']}, p_dict)

    def findPlansByEventType(self, event_type):
        retval = []
        plans = self.col.find({"events": event_type})
        for p in plans:
            p = from_mongo_id(p)
            p = Plan.fromDict(p)
            retval.append(p)
        return retval
