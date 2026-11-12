"""Run: python -m unittest discover -s tests -p '*_test.py'"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from features import normalize

class FeaturesTest(unittest.TestCase):
    def hand(self,offset=0):
        return [[offset+i*.02,i*.03,i*.001] for i in range(21)]
    def test_missing(self):
        self.assertIsNone(normalize([]))
    def test_feature_size_and_presence(self):
        self.assertEqual(len(normalize([self.hand()])),128)
        self.assertEqual(normalize([self.hand()])[-2:],[1.,0.])
        self.assertEqual(normalize([self.hand(),self.hand(1)])[-2:],[1.,1.])
    def test_translation_scale_invariance(self):
        import numpy as np
        hands=[self.hand(),self.hand(1)]
        changed=[(np.asarray(h)*2+np.array([3,4,0])).tolist() for h in hands]
        np.testing.assert_allclose(normalize(hands),normalize(changed),atol=1e-10)
    def test_degenerate(self):
        self.assertIsNone(normalize([[[0,0,0]]*21]))

if __name__=='__main__':unittest.main()
