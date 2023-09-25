import unittest
from loopback.loopback import ServiceCallbacks

class TestLoopbackService(unittest.TestCase):
    def test_calculate_ip_address(self):
        self.assertEqual('10.0.0.1', ServiceCallbacks.calculate_ip_address('10.0.0.0/24'))
        self.assertEqual('10.0.0.1', ServiceCallbacks.calculate_ip_address('10.0.0.0/24'))