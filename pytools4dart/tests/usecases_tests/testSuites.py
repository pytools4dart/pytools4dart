import unittest
from test_use_case1 import UseCase1Test

def suite():
    suite = unittest.TestSuite()
    suite.addTest(UseCase1Test("test_use_case_1"))
    suite.addTest(UseCase3Test("test_use_case_3"))
    return suite