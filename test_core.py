import unittest
from core import EventStore,VersionConflict
class Tests(unittest.TestCase):
    def test_version_and_hash(self):
        s=EventStore(); s.append('x',0,'created',{'n':1})
        self.assertTrue(s.verify('x'))
        with self.assertRaises(VersionConflict): s.append('x',0,'oops',{})

    def test_empty_stream(self):
        store = EventStore()
        self.assertEqual(store.read("missing"), [])
        self.assertTrue(store.verify("missing"))
