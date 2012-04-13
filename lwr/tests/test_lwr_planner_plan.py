import unittest

from lwr.planner.plan import Event, Job, Plan, JobTemplate

class TestEvent(unittest.TestCase):
    def test_simple_event(self):
        e = Event(owner='me', bucket='public', type='hg.pushes')

class TestJob(unittest.TestCase):
    def test_simple_job(self):
        e = Event(owner='me', bucket='public', type='hg.pushes')
        j = Job(owner='me', bucket='b1', command='echo hello world', state ='pending', results=None, event=e, interpreter='bash')

class TestPlan(unittest.TestCase):
    def test_plan_run(self):
        e = Event(owner='me', bucket='public', type='hg.pushes')
        jt = JobTemplate(command="echo hello world", interpreter="bash")
        p = Plan(owner='me', bucket='b1', events=["public.hg.pushes"], job_template=jt)
        j = p.run(e)
