import unittest
from main import TraceParent, parse_traceparent, extract_traceparent


VALID = '00-11111111111111111111111111111111-2222222222222222-01'


class TraceContextTests(unittest.TestCase):
    def test_round_trip_and_sampling(self):
        parsed = parse_traceparent(VALID)
        self.assertEqual(parsed.to_header(), VALID)
        self.assertTrue(parsed.sampled)
        self.assertFalse(parse_traceparent(VALID[:-2] + '00').sampled)

    def test_sampling_masks_only_low_bit(self):
        self.assertTrue(parse_traceparent(VALID[:-2] + '09').sampled)
        self.assertFalse(parse_traceparent(VALID[:-2] + '08').sampled)










if __name__ == '__main__':
    unittest.main()
