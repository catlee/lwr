import unittest
try:
    import pymongo
    from bson.objectid import ObjectId
except ImportError:
    from nose import SkipTest
    raise SkipTest

from lwr.plugins.mongodb.store import MongoPlannerStore
from lwr.planner.plan import Plan, JobTemplate

class TestMongoStore(unittest.TestCase):
    def setUp(self):
        # Clear out everything
        self.conn = pymongo.Connection()
        self.conn['lwr_test'].drop_collection('planners')

        self.s = MongoPlannerStore({'hosts': 'localhost', 'database': 'lwr_test', 'collection': 'planners'})

    def test_addPlan(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        _id = self.s.addPlan(p)
        self.assertIsNot(_id, None)

    def test_getPlan(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        _id = self.s.addPlan(p)

        p1 = self.s.getPlan(_id)

        self.assertEquals(p.asDict(), p1.asDict())

    def test_getPlan_missing(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        _id = self.s.addPlan(p)

        _id2 = str(ObjectId())

        self.assertNotEqual(_id, _id2)

        with self.assertRaises(KeyError):
            self.s.getPlan(str(_id2))

    def test_findPlansByBucket(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        self.s.addPlan(p)

        plans = self.s.findPlansByBucket('b1')

        self.assertEquals(len(plans), 1)
        self.assertEquals(plans[0].asDict(), p.asDict())

        plans = self.s.findPlansByBucket('b2')
        self.assertEquals(len(plans), 0)

    def test_findPlansByEventType(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        self.s.addPlan(p)

        plans = self.s.findPlansByEventType('hg.push')

        self.assertEquals(len(plans), 1)
        self.assertEquals(plans[0].asDict(), p.asDict())

        plans = self.s.findPlansByEventType('not-thre')
        self.assertEquals(len(plans), 0)

    def test_updatePlan(self):
        p = Plan(owner='me', bucket='b1', events=['hg.push'],
                job_template=JobTemplate(command='echo hello world', interpreter='bash'),
                )
        _id = self.s.addPlan(p)

        p1 = self.s.getPlan(_id)
        self.assertEquals(p1.owner, 'me')

        p.owner = 'you'
        self.s.updatePlan(p)

        p1 = self.s.getPlan(_id)
        self.assertEquals(p1.owner, 'you')
