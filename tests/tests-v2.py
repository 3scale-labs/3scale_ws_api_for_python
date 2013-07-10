""" Tests for the NEW way of using the plugin:
    app_id/app_key or user_key are sent in the
    method calls
"""
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

        self.ThreeScaleAuthRep = ThreeScalePY.ThreeScaleAuthRep
        self.ThreeScaleAuthorize = ThreeScalePY.ThreeScaleAuthorize
        self.ThreeScaleReport = ThreeScalePY.ThreeScaleReport
        self.ThreeScaleServerError = ThreeScalePY.ThreeScaleServerError
        self.ThreeScaleException = ThreeScalePY.ThreeScaleException
        self.ThreeScaleAuthorizeUserKey = ThreeScalePY.ThreeScaleAuthorizeUserKey
        self.ThreeScaleAuthRepUserKey = ThreeScalePY.ThreeScaleAuthRepUserKey

class TestThreeScaleAuthRep(TestThreeScale):
    """test case for authrep API call"""

    def setUp(self):
        """setUp for authrep API"""
        self.setupTests()

    def testAuthRepWithValidCredentials(self):
        """test authrep API with valid credentials"""
        authrep = self.ThreeScaleAuthRep(self.provider_key)

        self.assertTrue(authrep.authrep(self.app_id, self.app_key))

    def testAuthRepWithInvalidProviderKey(self):
        """test authrep API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        authrep = self.ThreeScaleAuthRep(provider_key)

        self.assertFalse(authrep.authrep(self.app_id, self.app_key))
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("provider key \"invalidProviderKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepWithInvalidAppId(self):
        """test authrep API with invalid app id"""
        app_id = 'invalidAppId'
        authrep = self.ThreeScaleAuthRep(self.provider_key)

        self.assertFalse(authrep.authrep(app_id, self.app_key))
        self.assertEquals(404, authrep.error_code)
        self.assertEquals("application with id=\"invalidAppId\" was not found", authrep.build_response().get_reason())

    def testAuthRepWithInvalidAppKey(self):
        """test authrep API with invalid app key"""
        app_key = 'invalidAppKey'
        authrep = self.ThreeScaleAuthRep(self.provider_key)

        self.assertFalse(authrep.authrep(self.app_id, app_key))
        self.assertEquals(409, authrep.error_code)
        self.assertEquals("application key \"invalidAppKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepWithMissingAppKey(self):
        """test authrep API with missing app key"""
        authrep = self.ThreeScaleAuthRep(self.provider_key)

        self.assertFalse(authrep.authrep(self.app_id))
        self.assertEquals(409, authrep.error_code)
        self.assertEquals("application key is missing", authrep.build_response().get_reason())

    def testAuthRepWithInvalidMetric(self):
        """test authrep API with invalid metric"""
        authrep = self.ThreeScaleAuthRep(self.provider_key)

        self.assertFalse(authrep.authrep(self.app_id, self.app_key, {"invalid_metric":1}, {'request': "bdsad"}))
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("metric \"invalid_metric\" is invalid", authrep.build_response().get_reason())

class TestThreeScaleAuthRepUserKey(TestThreeScale):
    """test case for authrep API call"""

    def setUp(self):
        """setUp for authrep API"""
        self.setupTests()

    def testAuthRepUserKeyWithValidCredentials(self):
        """test authrep API with valid credentials"""
        authrep = self.ThreeScaleAuthRepUserKey(self.provider_key)

        self.assertTrue(authrep.authrep(self.user_key))

    def testAuthRepUserKeyWithInvalidProviderKey(self):
        """test authrep API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        authrep = self.ThreeScaleAuthRepUserKey(provider_key)

        self.assertFalse(authrep.authrep(self.user_key))
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("provider key \"invalidProviderKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepUserKeyWithInvalidUserKey(self):
        """test authrep API with invalid user key"""
        user_key = 'invalidUserKey'
        authrep = self.ThreeScaleAuthRepUserKey(self.provider_key)

        self.assertFalse(authrep.authrep(user_key))
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("user key \"invalidUserKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepUserKeyWithInvalidMetric(self):
        """test authrep API with invalid metric"""
        authrep = self.ThreeScaleAuthRepUserKey(self.provider_key)

        self.assertFalse(authrep.authrep(self.user_key, {"invalid_metric":1}, {'request': "bdsad"}))
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("metric \"invalid_metric\" is invalid", authrep.build_response().get_reason())

class TestThreeScaleAuthorize(TestThreeScale):
    """test case for authorize API call"""

    def setUp(self):
        """setUp for authorize API"""
        self.setupTests()

    def testAuthorizeWithValidCredentials(self):
        """test authorize API with valid credentials"""
        auth = self.ThreeScaleAuthorize(self.provider_key)

        self.assertTrue(auth.authorize(self.app_id, self.app_key))

    def testAuthorizeWithInvalidAppId(self):
        """test authorize API with invalid app id"""
        app_id = 'invalidAppId'
        auth = self.ThreeScaleAuthorize(self.provider_key)

        try:
            auth.authorize(app_id, self.app_key)
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeWithInvalidProviderKey(self):
        """test authorize API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        auth = self.ThreeScaleAuthorize(provider_key)

        try:
            auth.authorize(self.app_id, self.app_key)
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeResponsePlan(self):
        """test authorize API response (plan)"""
        auth = self.ThreeScaleAuthorize(self.provider_key)

        plan = 'Testing'
        if auth.authorize(self.app_id, self.app_key):
            resp = auth.build_auth_response()
            self.assertEquals(resp.get_plan(), plan)

    def testAuthorizeResponseUsageReport(self):
        """test authorize API response usage report (metric)"""
        auth = self.ThreeScaleAuthorize(self.provider_key)

        metric = 'hits'
        if not auth.authorize(self.app_id, self.app_key):
            self.fail('Not authorized')
        resp = auth.build_auth_response()
        reports = resp.get_usage_reports()
        self.assertEquals(reports[0].get_metric(), metric)


class TestThreeScaleAuthorizeUserKey(TestThreeScale):
    """test case for authorize API call with User Key"""

    def setUp(self):
        """setUp for authorize API"""
        self.setupTests()

    def testAuthorizeUserKeyWithValidCredentials(self):
        """test authorize API with valid credentials"""
        auth = self.ThreeScaleAuthorizeUserKey(self.provider_key)
        self.assertTrue(auth.authorize(self.user_key))

    def testAuthorizeUserKeyWithInvalidAppId(self):
        """test authorize API with invalid user key"""
        user_key = 'invalidAppId'
        auth = self.ThreeScaleAuthorizeUserKey(self.provider_key)

        try:
            auth.authorize(user_key)
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeUserKeyWithInvalidProviderKey(self):
        """test authorize API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        auth = self.ThreeScaleAuthorizeUserKey(provider_key)

        try:
            auth.authorize(self.user_key)
        except self.ThreeScaleServerError, err:
            self.assert_(True, True)

    def testAuthorizeUserKeyResponsePlan(self):
        """test authorize API response (plan)"""
        auth = self.ThreeScaleAuthorizeUserKey(self.provider_key)

        plan = 'Testing'
        if auth.authorize(self.user_key):
            resp = auth.build_auth_response()
            self.assertEquals(resp.get_plan(), plan)

    def testAuthorizeUserKeyResponseUsageReport(self):
        """test authorize API response usage report (metric)"""
        auth = self.ThreeScaleAuthorizeUserKey(self.provider_key)

        metric = 'hits'
        if not auth.authorize(self.user_key):
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
    exec_type = 'all' # argv[1] can be: authrep, authorize, report, all
    if len(sys.argv) == 2:
        exec_type = sys.argv[1]

    auth_tests = [
                   'testAuthorizeWithInvalidAppId',
                   'testAuthorizeWithInvalidProviderKey',
                   'testAuthorizeWithValidCredentials',
                   'testAuthorizeResponsePlan',
                   'testAuthorizeResponseUsageReport',
                 ]

    auth_userkey_tests = [
                     'testAuthorizeUserKeyWithValidCredentials',
                     'testAuthorizeUserKeyWithInvalidAppId',
                     'testAuthorizeUserKeyWithInvalidProviderKey',
                     'testAuthorizeUserKeyResponsePlan',
                     'testAuthorizeUserKeyResponseUsageReport'
                     ]

    authrep_userkey_tests = [
                      'testAuthRepUserKeyWithValidCredentials',
                      'testAuthRepUserKeyWithInvalidProviderKey',
                      'testAuthRepUserKeyWithInvalidUserKey',
                      'testAuthRepUserKeyWithInvalidMetric',
                    ]

    if exec_type in ('all', 'authorize'):
        suite = unittest.TestSuite(map(TestThreeScaleAuthorize, auth_tests))
    elif exec_type in ('user_key'):
        suite = unittest.TestSuite(map(TestThreeScaleAuthorizeUserKey, auth_userkey_tests))
        for test in authrep_userkey_tests:
            suite.addTest(TestThreeScaleAuthRepUserKey(test))
    else:
        suite = unittest.TestSuite()

    authrep_tests = [
                      'testAuthRepWithValidCredentials',
                      'testAuthRepWithInvalidProviderKey',
                      'testAuthRepWithInvalidAppId',
                      'testAuthRepWithInvalidAppKey',
                      'testAuthRepWithMissingAppKey',
                      'testAuthRepWithInvalidMetric',
                    ]

    for test in authrep_tests:
        if exec_type in ('all', 'authrep'):
            suite.addTest(TestThreeScaleAuthRep(test))

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