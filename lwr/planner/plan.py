from lwr.lib.entities.base import VersionedEntity, LoggedEntityMixin
from lwr.events import Event

class Job(VersionedEntity, LoggedEntityMixin):
    v = 0
    __slots__ = ('id', 'owner', 'bucket',
                 'command', 'command_url', 'state', 'results', 'data', 'event',
                 'tags', 'interpreter', 'times',
                 'required_slave_tags',
                 'log', 'sigs')
    __defaults__ = {
            'data': None,
            'log': [],
            'tags': [],
            'command_url': None,
            'required_slave_tags': [],
            'sigs': None,
            'id': None,
            'times': {},
            }
    __nested_types__ = {
            'event': Event,
            }

class JobTemplate(VersionedEntity):
    # Like a job without lots of pesky details
    v = 0
    __slots__ = (set(Job.__slots__) -
                 set(('owner', 'bucket', 'state', 'results', 'event', 'times', 'log', 'sigs')))
    __defaults__ = Job.__defaults__

class Plan(VersionedEntity):
    v = 0
    __slots__ = ('id', 'owner', 'bucket', 'events', 'job_template', 'data')
    __defaults__ = {
            'data': None,
            'id': None,
            }
    __nested_types__ = {
            'job_template': JobTemplate,
            }

    def run(self, event):
        job_dict = self.job_template.asDict()
        job_dict['event'] = event
        if self.data:
            job_dict['data'] = self.data.copy()
        job_dict['bucket'] = self.bucket
        job_dict['owner'] = self.owner
        job_dict['state'] = 'pending'
        job_dict['results'] = None
        job_dict['times'] = {}
        job_dict['logs'] = []
        job = Job.fromDict(job_dict)
        job.addLog({"created_by": self.asDict()})
        return job
