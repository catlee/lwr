from unittest import TestCase

from lwr.config import pluginFromDict, dictFromSection

from lwr.events.interface import EventStore

class TestConfigFile(TestCase):
    def test_dictFromSection(self):
        pass

class TestPluginFromDict(TestCase):
    def test_dummy(self):
        d = {'plugin': 'lwr.plugins.dummy', 'foo': 'bar'}
        p = pluginFromDict(d, EventStore)

        self.assertEquals(p.config, d)

    def test_dummy_byname(self):
        d = {'plugin': 'lwr.plugins.dummy.store:DummyEventStore', 'foo': 'bar'}
        p = pluginFromDict(d, EventStore)

        self.assertEquals(p.config, d)
