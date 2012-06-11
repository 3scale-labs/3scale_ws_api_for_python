# -*- coding: utf-8 -*-
import os
import sys

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASEDIR)

#!/usr/bin/env python -I ../

import unittest
import time

import ThreeScalePY

class TestThreeScale(unittest.TestCase):
    """base class for testing authorize and report APIs"""
    def setupTests(self):
        # credentials used for testing the code
        self.app_id = os.environ['TEST_3SCALE_APP_ID'] # or set app id here
        self.app_key = os.environ['TEST_3SCALE_APP_KEY'] # or set app key here
        self.provider_key = os.environ['TEST_3SCALE_PROVIDER_KEY'] # or set provider key here

        self.ThreeScaleAuthorize = ThreeScalePY.ThreeScaleAuthorize
        self.ThreeScaleReport = ThreeScalePY.ThreeScaleReport
        self.ThreeScaleServerError = ThreeScalePY.ThreeScaleServerError
        self.ThreeScaleException = ThreeScalePY.ThreeScaleException

class TestThreeScaleAuthorize(TestThreeScale):
    """test case for authorize API call"""

    def setUp(self):
        """setUp for authorize API"""
        self.setupTests()
  
    def testAuthorizeWithValidCredentials(self):
        """test authorize API with valid credentials"""
        auth = self.ThreeScaleAuthorize(self.provider_key, 
                                        self.app_id, 
                                        self.app_key)
        self.assertTrue(auth.authorize())

    def testAuthorizeWithInvalidAppId(self):
        """test authorize API with invalid app id"""
        app_id = 'invalidAppId'
        auth = self.ThreeScaleAuthorize(self.provider_key, 
                                        app_id, 
                                        self.app_key)
        try:
            auth.authorize()
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeWithInvalidProviderKey(self):
        """test authorize API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        auth = self.ThreeScaleAuthorize(provider_key, 
                                        self.app_id, 
                                        self.app_key)
        try:
            auth.authorize()
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeResponsePlan(self):
        """test authorize API response (plan)"""
        auth = self.ThreeScaleAuthorize(self.provider_key, 
                                        self.app_id, 
                                        self.app_key)
        plan = 'Testing'
        if auth.authorize():
            resp = auth.build_auth_response()
            self.assertEquals(resp.get_plan(), plan)

    def testAuthorizeResponseUsageReport(self):
        """test authorize API response usage report (metric)"""
        auth = self.ThreeScaleAuthorize(self.provider_key, 
                                        self.app_id, 
                                        self.app_key)
        metric = 'hits'
        if not auth.authorize():
            self.fail('Not authorized')
        resp = auth.build_auth_response()
        reports = resp.get_usage_reports()
        self.assertEquals(reports[0].get_metric(), metric)


class TestThreeScaleReport(TestThreeScale):
    """test case for report API call"""

    def setUp(self):
        """setUp for report API"""
        self.setupTests()
  
    def testReportWithInvalidProviderKey(self):
        """test report API with invalid provider key"""

        provider_key = 'invalidProviderKey'
        report = self.ThreeScaleReport(provider_key)
        t1 = {}
        trans_usage = {}
        trans_usage['hits'] = 1
        trans_usage['max_value'] = 5
        t1['app_id'] = self.app_id
        t1['usage'] = trans_usage
        trans_usage['timestamp'] = time.gmtime(time.time())

        transactions = [t1]
        try:
            report.report(transactions)
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testReportWithInvalidTimestamp(self):
        """test report API with invalid timestamp"""
        report = self.ThreeScaleReport(self.provider_key)
        t1 = {}
        trans_usage = {}
        trans_usage['hits'] = 1
        trans_usage['max_value'] = 5
        t1['app_id'] = self.app_id
        t1['usage'] = trans_usage
        trans_usage['timestamp'] = 'invalidTimeStamp'

        transactions = [t1]
        try:
            report.report(transactions)
        except self.ThreeScaleException, err:
            self.assert_(True, True)

    def testReportWithOneTransaction(self):
        """test report API with one transaction"""
        report = self.ThreeScaleReport(self.provider_key)
        t1 = {}
        trans_usage = {}
        trans_usage['hits'] = 1
        trans_usage['max_value'] = 5
        t1['app_id'] = self.app_id
        t1['usage'] = trans_usage
        trans_usage['timestamp'] = time.gmtime(time.time())

        transactions = [t1]
        self.assertTrue(report.report(transactions))

    def testReportWithTwoTransactions(self):
        """test report API with two transactions"""
        report = self.ThreeScaleReport(self.provider_key)
        t1 = {}
        trans_usage = {}
        trans_usage['hits'] = 1
        trans_usage['max_value'] = 5
        t1['app_id'] = self.app_id
        trans_usage['timestamp'] = time.gmtime(time.time())
        t1['usage'] = trans_usage
        t2 = {}
        trans_usage = {}
        trans_usage['hits'] = 2
        trans_usage['timestamp'] = time.gmtime(time.time())
        trans_usage['max_value'] = 2
        t2['app_id'] = self.app_id
        t2['usage'] = trans_usage

        transactions = [t1, t2]
        self.assertTrue(report.report(transactions))

if __name__ == '__main__':
    exec_type = 'all' # argv[1] can be: authorize, report, all
    if len(sys.argv) == 2:
        exec_type = sys.argv[1]
    auth_tests = [
                   'testAuthorizeWithInvalidAppId',
                   'testAuthorizeWithInvalidProviderKey',
                   'testAuthorizeWithValidCredentials',
                   'testAuthorizeResponsePlan',
                   'testAuthorizeResponseUsageReport',
                 ]

    if exec_type in ('all', 'authorize'):
        suite = unittest.TestSuite(map(TestThreeScaleAuthorize, auth_tests))
    else:
        suite = unittest.TestSuite()

    report_tests = [
                     'testReportWithInvalidProviderKey',
                     'testReportWithInvalidTimestamp',
                     'testReportWithOneTransaction',
                     'testReportWithTwoTransactions',
                   ]
    for test in report_tests:
        if exec_type in ('all', 'report'):
            suite.addTest(TestThreeScaleReport(test))

    unittest.TextTestRunner(verbosity=2).run(suite)
