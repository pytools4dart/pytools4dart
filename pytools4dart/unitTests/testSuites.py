import unittest
from test_use_case1 import UseCase1Test
from test_use_case3 import UseCase3Test
import test_use_case1, test_use_case3

def suite():
    suite = unittest.TestSuite()
    suite.addTest(UseCase1Test())
    suite.addTest(UseCase3Test())
    return suite