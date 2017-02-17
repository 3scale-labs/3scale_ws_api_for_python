# -*- coding: utf-8 -*-
import os
import sys

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASEDIR)

#!/usr/bin/env python -I ../

import unittest
import time
import httpretty

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

class TestThreeScaleAuthRep(TestThreeScale):
    """test case for authrep API call"""

    def setUp(self):
        """setUp for authrep API"""
        self.setupTests()

    def testAuthRepWithValidCredentials(self):
        """test authrep API with valid credentials"""
        authrep = self.ThreeScaleAuthRep(self.provider_key,
                                         self.app_id,
                                         self.app_key)
        self.assertTrue(authrep.authrep())

    def testAuthRepWithInvalidProviderKey(self):
        """test authrep API with invalid provider key"""
        provider_key = 'invalidProviderKey'
        authrep = self.ThreeScaleAuthRep(provider_key,
                                         self.app_id,
                                         self.app_key)

        self.assertFalse(authrep.authrep())
        self.assertEquals(403, authrep.error_code)
        self.assertEquals("provider key \"invalidProviderKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepWithInvalidAppId(self):
        """test authrep API with invalid app id"""
        app_id = 'invalidAppId'
        authrep = self.ThreeScaleAuthRep(self.provider_key,
                                         app_id,
                                         self.app_key)
        self.assertFalse(authrep.authrep())
        self.assertEquals(404, authrep.error_code)
        self.assertEquals("application with id=\"invalidAppId\" was not found", authrep.build_response().get_reason())

    def testAuthRepWithInvalidAppKey(self):
        """test authrep API with invalid app key"""
        app_key = 'invalidAppKey'
        authrep = self.ThreeScaleAuthRep(self.provider_key,
                                         self.app_id,
                                         app_key)
        self.assertFalse(authrep.authrep())
        self.assertEquals(409, authrep.error_code)
        self.assertEquals("application key \"invalidAppKey\" is invalid", authrep.build_response().get_reason())

    def testAuthRepWithMissingAppKey(self):
        """test authrep API with missing app key"""
        app_key = 'invalidAppKey'
        authrep = self.ThreeScaleAuthRep(self.provider_key,
                                         self.app_id)

        self.assertFalse(authrep.authrep())
        self.assertEquals(409, authrep.error_code)
        self.assertEquals("application key is missing", authrep.build_response().get_reason())

    def testAuthRepWithInvalidMetric(self):
        """test authrep API with invalid metric"""
        authrep = self.ThreeScaleAuthRep(self.provider_key, self.app_id, self.app_key)

        self.assertFalse(authrep.authrep({"invalid_metric":1}))
        self.assertEquals(404, authrep.error_code)
        self.assertEquals("metric \"invalid_metric\" is invalid", authrep.build_response().get_reason())


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
        plan = 'Basic'
        if auth.authorize():
            resp = auth.build_auth_response()
            self.assertEquals(resp.get_plan(), plan)

    @httpretty.activate
    def testAuthorizeResponseUsageReport(self):
        """test parsing usage reports"""
        xml_body = """<status>
              <authorized>false</authorized>
              <reason>usage limits are exceeded</reason>
              <plan>Ultimate</plan>
              <usage_reports>
                <usage_report metric="hits" period="day" exceeded="true">
                  <period_start>2010-04-26 00:00:00 +0000</period_start>
                  <period_end>2010-04-27 00:00:00 +0000</period_end>
                  <current_value>50002</current_value>
                  <max_value>50000</max_value>
                </usage_report>
                <usage_report metric="hits" period="month">
                  <period_start>2010-04-01 00:00:00 +0000</period_start>
                  <period_end>2010-05-01 00:00:00 +0000</period_end>
                  <current_value>999872</current_value>
                  <max_value>150000</max_value>
                </usage_report>
              </usage_reports>
            </status>"""
        auth = self.ThreeScaleAuthorize(self.provider_key, "foo", "bar")            
        uri = "%s/transactions/authorize.xml?provider_key=1234abcd&app_id=foo" % (auth.get_base_url())
        httpretty.register_uri(httpretty.GET, uri, status=200, body=xml_body)
        
        self.assertTrue(auth.authorize())

        resp = auth.build_auth_response()
        reports = resp.get_usage_reports()
        self.assertEquals(reports[0].get_metric(), "hits")
        self.assertEquals(reports[0].get_period(), "day")
        self.assertEquals(reports[0].get_start_period(), "2010-04-26 00:00:00 +0000")
        self.assertEquals(reports[0].get_end_period(), "2010-04-27 00:00:00 +0000")
        self.assertEquals(reports[0].get_max_value(), "50000")
        self.assertEquals(reports[0].get_current_value(), "50002")

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
                   'testAuthorizeResponseUsageReport'
                 ]

    if exec_type in ('all', 'authorize'):
        suite = unittest.TestSuite(map(TestThreeScaleAuthorize, auth_tests))
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

    result = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(not result)
