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

    def test_zero_identifiers_rejected(self):
        for value in (VALID.replace('1' * 32, '0' * 32), VALID.replace('2' * 16, '0' * 16)):
            with self.subTest(value=value), self.assertRaises(ValueError): parse_traceparent(value)

    def test_uppercase_whitespace_and_extra_fields_rejected(self):
        for value in (VALID.replace('1', 'A', 1), ' ' + VALID, VALID + '\n', VALID + '-extra', VALID[:-1]):
            with self.subTest(value=value), self.assertRaises(ValueError): parse_traceparent(value)

    def test_unsupported_versions_rejected(self):
        for version in ('01', 'ff'):
            with self.subTest(version=version), self.assertRaises(ValueError): parse_traceparent(version + VALID[2:])

    def test_case_insensitive_header_name(self):
        self.assertEqual(extract_traceparent({'TraceParent': VALID}).to_header(), VALID)
        self.assertIsNone(extract_traceparent({'accept': 'application/json'}))

    def test_duplicate_case_variant_headers_rejected(self):
        with self.assertRaises(ValueError): extract_traceparent({'TraceParent': VALID, 'traceparent': VALID})

    def test_child_preserves_trace_changes_parent_and_clears_reserved_flags(self):
        parent = parse_traceparent(VALID[:-2] + '09')
        child = parent.child('3333333333333333', sampled=False)
        self.assertEqual(child.trace_id, parent.trace_id)
        self.assertNotEqual(child.parent_id, parent.parent_id)
        self.assertEqual(child.flags, 0)
        self.assertEqual(parent.flags, 9)




if __name__ == '__main__':
    unittest.main()
