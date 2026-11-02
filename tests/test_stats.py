import unittest
from rewardbench.stats import paired_bootstrap_delta

class StatsTests(unittest.TestCase):
    def test_bootstrap_reproducible(self):
        pairs = [(1.0, 0.5)]*20
        a = paired_bootstrap_delta(pairs)
        b = paired_bootstrap_delta(pairs)
        self.assertEqual(a, b)
        self.assertEqual(a['delta_mean'], .5)
        self.assertEqual(a['bootstrap_95_ci'], [.5, .5])

    def test_nonfinite_inputs_rejected(self):
        for value in (float('nan'), float('inf'), float('-inf'), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                paired_bootstrap_delta([(value, 0.5), (0.5, 0.5)])

    def test_insufficient_data_and_invalid(self):
        self.assertIsNone(paired_bootstrap_delta([(1.0, 0.0)]))
        with self.assertRaises(ValueError):
            paired_bootstrap_delta([(2.0, 0.0), (1.0, 0.0)])

if __name__ == '__main__':
    unittest.main()
