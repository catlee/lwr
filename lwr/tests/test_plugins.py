import unittest

import os.path

from lwr.plugins import load_plugin
from lwr.events.interface import EventStore

class TestPluginLoading(unittest.TestCase):
    def test_load_module(self):
        p = load_plugin("lwr.plugins.dummy", EventStore)
        self.assertTrue(issubclass(p, EventStore))

    def test_load_module_notfound(self):
        with self.assertRaises(ImportError):
            load_plugin("lwr.plugins.XXX", EventStore)

    def test_load_file(self):
        p = load_plugin(os.path.join(os.path.dirname(__file__), "../plugins/dummy/store.py"), EventStore)
        self.assertTrue(issubclass(p, EventStore))

    def test_load_file_notfound(self):
        with self.assertRaises(ImportError):
            load_plugin(os.path.join(os.path.dirname(__file__), "../plugins/dummy/XXX.py"), EventStore)

    def test_load_module_byname(self):
        p = load_plugin("lwr.plugins.dummy", object_name="DummyEventStore")
        self.assertTrue(issubclass(p, EventStore))

    def test_load_file_byname(self):
        p = load_plugin(os.path.join(os.path.dirname(__file__), "../plugins/dummy/store.py"), object_name="DummyEventStore")
        self.assertTrue(issubclass(p, EventStore))
