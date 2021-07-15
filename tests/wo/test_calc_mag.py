import os
import unittest

from obspy import read

from wo.magnitude import compute_magnitude_all

DATA_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'data')


class CalculateMagnitudeTest(unittest.TestCase):

    def test_calc_mag(self):
        st = read(os.path.join(DATA_DIR, 'stream.msd'))

        mag = compute_magnitude_all(st)
        self.assertEqual(mag['count_deles'], 1700)
        self.assertEqual(mag['count_labuhan'], 46674)
        self.assertEqual(mag['count_pasarbubar'], 230603)
        self.assertEqual(mag['count_pusunglondon'], 16056)

        self.assertAlmostEqual(mag['ml_deles'], 1.4798585246567297, places=4)
        self.assertAlmostEqual(mag['ml_labuhan'], 1.625597499326541, places=4)
        self.assertAlmostEqual(mag['ml_pasarbubar'],
                               2.158377027093737, places=4)
        self.assertAlmostEqual(
            mag['ml_pusunglondon'], 2.1240845696276773, places=4)


if __name__ == '__main__':
    unittest.main()
