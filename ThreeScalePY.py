"""Python API for 3scale Service Management API.

The Python API to interact with 3scale Service Management API account. The library supports 
the 3 main calls to the 3scale Service Management API:
 - authrep()
 - authorize()
 - report()

 AuthRep GET API usage:
---------------------
    # app_id or oauth authentication modes
    authrep = ThreeScalePY.ThreeScaleAuthRep(app_id = 'your_app_id', app_key = 'your_app_key', 
                              service_id = 'your_service_id', service_token = 'your_service_token')
    if authrep.authrep():
        # all was ok, proceed normally
    else: # something was wrong
        sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())

    # user_key authentication mode
    authrep = ThreeScalePY.ThreeScaleAuthRepUserKey(user_key = 'your_user_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
    if authrep.authrep():
        # all was ok, proceed normally
    else: # something was wrong
        sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())

 Authorize GET API usage:
---------------------
    auth = ThreeScalePY.ThreeScaleAuthorize(app_id = 'your_app_id', app_key = 'your_app_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
    if auth.authorize():
        resp = auth.build_auth_response()
        usage_reports = resp.get_usage_reports()
        for report in usage_reports:
            print "            metric => %s" % report.get_metric()
            print "            period => %s" % report.get_period()
            print "            start => %s" % report.get_start_period()
            print "            end => %s" % report.get_end_period()
            print "            max => %s" % report.get_max_value()
            print "            current => %s" % report.get_current_value()

    auth = ThreeScalePY.ThreeScaleAuthorizeUserKey(user_key = 'your_user_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
    if auth.authorize():
        resp = auth.build_auth_response()
        usage_reports = resp.get_usage_reports()
        for report in usage_reports:
            print "            metric => %s" % report.get_metric()
            print "            period => %s" % report.get_period()
            print "            start => %s" % report.get_start_period()
            print "            end => %s" % report.get_end_period()
            print "            max => %s" % report.get_max_value()
            print "            current => %s" % report.get_current_value()

Report POST API usage:
-------------------------
    t1 = {}
    trans_usage = {}
    trans_usage['hits'] = 1
    trans_usage['custom_metric'] = 5
    t1['usage'] = trans_usage
    t1['timestamp'] = time.gmtime(time.time())
    t1['app_id'] = 'your_app_id' # OR t1['user_key'] = 'your_user_key'
    transactions = [t1]

    report = ThreeScalePY.ThreeScaleReport(service_id = 'your_service_id', service_token = 'your_service_token')
    resp = report.report(transactions)
"""

import time
from lxml import etree

try:
    # Python 3
    from urllib.parse import urlencode, quote, urlparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    # Python 2
    from urllib import urlencode, quote
    from urllib2 import urlopen, Request, HTTPError, URLError
    from urlparse import urlparse

__version__ = '2.6.0'

__all__ = ['ThreeScale',
           'ThreeScaleAuthRep', 'ThreeScaleAuthRepUserKey', 'ThreeScaleAuthRepResponse', 
           'ThreeScaleAuthorize', 'ThreeScaleAuthorizeUserKey', 'ThreeScaleAuthorizeResponse',
           'ThreeScaleReport', 'ThreeScaleAuthorizeResponseUsageReport'
          ]

class ThreeScale:

    DEFAULT_BACKEND_URI = 'https://su1.3scale.net:443'
    ENCODING = 'utf-8'

    def validate_backend_uri(self, uri):
        parsed = urlparse(uri)
        valid = True if parsed.scheme in ['http','https'] and parsed.netloc else False
        return valid

    """The base class to initialize the credentials and URLs"""
    def __init__(self, provider_key="", app_id="", app_key="", user_key="", service_id="", service_token="", backend_uri=""):
        """initialize the following credentials:
        - provider key
        - application id
        - application key
        - user key
        - service_id
        - service_token

        The application id and key are optional. If it is omitted, the
        provider key alone is set. This is useful when the class is
        inherited by ThreeScaleReport class, for which application id
        is passed in transactions data structure and application key
        is not necessary.

        @throws ThreeScaleException error, if neither provider_key nor service_token + service_id are
        provided.

        """

        if backend_uri and not self.validate_backend_uri(backend_uri):
            raise ThreeScaleException("The backend URI '%s' is invalid" % backend_uri)

        self.backend_uri = backend_uri or ThreeScale.DEFAULT_BACKEND_URI

        self.app_id = app_id
        self.app_key = app_key
        self.user_key = user_key
        self.provider_key = provider_key
        self.service_id = service_id
        self.service_token = service_token

        err = []
        if not provider_key and not (service_id and service_token):
            err.append("Provider key or service token and service ID must be defined")
            raise ThreeScaleException(': '.join(err))

    def get_base_url(self):
        """return the base url for using with authorize and report
        APIs"""
        return self.backend_uri

    def get_authrep_url(self):
        """return the url for passing authrep GET request"""
        auth_url = "%s/transactions/authrep.xml" % self.get_base_url()
        return auth_url

    def get_auth_url(self):
        """return the url for passing authorize GET request"""
        auth_url = "%s/transactions/authorize.xml" % self.get_base_url()
        return auth_url

    def get_report_url(self):
        """return the url for passing report POST request"""
        report_url = "%s/transactions.xml" % self.get_base_url()
        return report_url

    def dict_to_params(self, dict, param):
        """This method rebuilds hash parameters to be correctly encoded later for URL.
        e.g. usage dictionary {'hits':1} is turned into {"usage[hits]:1}."""
        dict_params = {}
        for key in list(dict.keys()):
          k = "%s[%s]" % (param, key)
          dict_params[k] = dict[key]
        return dict_params

    def get_query_string(self, other_params = {}, usage = {}, log = {}):
        """get the url encoded query string"""

        params = {}
        keys = ['app_id', 'app_key', 'user_key', 'provider_key', 'service_id', 'service_token']

        for key in keys:
            value = self.__dict__[key]
            if value:
                params[key] = value

        if other_params:
            params.update(other_params)
        if usage:
            params.update(self.dict_to_params(usage, "usage"))
        if log:
            params.update(self.dict_to_params(log, "log"))

        return urlencode(params)

    def add_version_header(self, req):
        version_header = "plugin-python-v%s" % __version__
        req.add_header('X-3scale-User-Agent', version_header)    

class ThreeScaleAuthRep(ThreeScale):
    """ThreeScaleAuthRep(): The derived class for ThreeScale. It is
    main class to invoke authrep GET API."""

    def validate(self):
        """validate the arguments. If any of following parameters is
        missing, exit from the script.
        - application id
        - provider key

        @throws ThreeScaleException error, if any of the credentials are
        invalid.
        """
        err = []
        if not self.app_id:
            err.append("App Id not defined")

        if len(err):
            raise ThreeScaleException(': '.join(err))

    def authrep(self, usage = { 'hits': 1 }, other_params = {}, log = {}, timeout = 10):
        """authrep() -- invoke authrep GET request.
        - usage passes the usage of each metric of your API.
        - other_params passes other parameters to the authrep call, e.g.
          service_id, user_id, a.s.o.
        - log passes log parameter details
        Read more details about AuthRep's parameters here: https://support.3scale.net/docs/3scale-apis-activedocs

        The authrep response is stored in a class variable.

        returns True, if AuthRep was successful (i.e. HTTP status is 200).
        @throws ThreeScaleServerError error, if invalid response is
        received.
        @throws ThreeScaleConnectionError error, if connection can not be
        established.
        @throws ThreeScaleException error, if any other unknown error is
        occurred while receiving response for authrep GET api.
        """
        self.authrepd = False
        self.authrep_xml = None

        self.validate()
        authrep_url = self.get_authrep_url()
        query_str = self.get_query_string(other_params, usage, log)

        query_url = "%s?%s" % (authrep_url, query_str)

        try:
            req = Request(query_url)
            self.add_version_header(req)
            resp = urlopen(req, timeout=timeout).read()
            self.authrepd = True
            self.authrep_xml = resp
            return True
        except HTTPError as err:
            if err.code in [403, 404, 409]:
               self.authrepd    = False
               self.error_code  = err.code
               self.authrep_xml = err.read()
               return False

            raise ThreeScaleServerError("Invalid response for url "
                                        "%s: %s" % (authrep_url, err))
        except URLError as err:
            raise ThreeScaleConnectionError("Connection error %s: "
                                        "%s" % (authrep_url, err))
        except Exception as err:
            # handle all other exceptions
            raise ThreeScaleException("Unknown error %s: "
                                        "%s" % (authrep_url, err))

    def build_response(self):
        """
        Store the xml response from authrep GET api in a Python
        object, ThreeScaleAuthRepResponse. The values in xml output
        can be retrived using the class methods.

        @returns ThreeScaleAuthRepResponse object.
        @throws ThreeScaleException error, if xml output received from
        the server is not valid.
        """

        xml = None
        resp = ThreeScaleAuthRepResponse()

        try:
            xml = etree.fromstring(self.authrep_xml)
        except Exception as err:
            raise ThreeScaleException("Invalid xml %s" % err)

        if not self.authrepd:
            if self.error_code == 409:
                resp.set_reason(xml.xpath('/status/reason')[0].text)
            elif self.error_code == 403 or self.error_code == 404:
                resp.set_reason(xml.xpath('/error')[0].text)
        return resp


class ThreeScaleAuthRepResponse():
    """The derived class for ThreeScale() class. The object constitutes
    the xml data retrived from authrep GET api."""
    def __init__(self):
        self.reason = None

    def set_reason(self, reason):
        self.reason = reason

    def get_reason(self):
        return self.reason


class ThreeScaleAuthRepUserKey(ThreeScaleAuthRep):
    """ThreeScaleAuthRepUserKey(): class to invoke authrep with user_key auth pattern GET API."""

    def __init__(self, provider_key="", user_key="", service_id="", service_token="", backend_uri=""):
        ThreeScaleAuthRep.__init__(self, provider_key, None, None, user_key, service_id, service_token, backend_uri)

    def validate(self):
        """validate the arguments. If any of following parameters is
        missing, exit from the script.
        - user key
        - provider key

        @throws ThreeScaleException error, if any of the credentials are
        invalid.
        """
        err = []
        if not self.user_key:
            err.append("User key not defined")

        if len(err):
            raise ThreeScaleException(': '.join(err))


class ThreeScaleAuthorize(ThreeScale):
    """ThreeScaleAuthorize(): The derived class for ThreeScale. It is
    main class to invoke authorize GET API."""

    def validate(self):
        """validate the arguments. If any of following parameters is
        missing, exit from the script.
        - application id
        - application key
        - provider key

        @throws ThreeScaleException error, if any of the credentials are
        invalid.
        """
        err = []
        if not self.app_id:
            err.append("App Id not defined")

        if len(err):
            raise ThreeScaleException(': '.join(err))

    def authorize(self, timeout = 10, usage = { 'hits': 1 }, other_params = {}):
        """authorize() -- invoke authorize GET request.
        - usage passes the usage of each metric of your API.
        - other_params passes other parameters to the authrep call, e.g.
          service_id, user_id, a.s.o.

        The authorize response is stored in a class variable.

        returns True, if authorization is successful.
        @throws ThreeScaleServerError error, if invalid response is
        received.
        @throws ThreeScaleConnectionError error, if connection can not be
        established.
        @throws ThreeScaleException error, if any other unknown error is
        occurred while receiving response for authorize GET api.
        """
        self.authorized = False
        self.auth_xml = None

        self.validate()
        auth_url = self.get_auth_url()
        query_str = self.get_query_string(other_params, usage)

        query_url = "%s?%s" % (auth_url, query_str)

        try:
            req = Request(query_url)
            self.add_version_header(req)
            resp = urlopen(req, timeout=timeout).read()
            self.authorized = True
            self.auth_xml = resp
            return True
        except HTTPError as err:
            if err.code in [403, 404, 409]:
               self.authorized = False
               self.error_code  = err.code
               self.auth_xml = err.read()
               return False

            raise ThreeScaleServerError("Invalid response for url "
                                        "%s: %s" % (auth_url, err))
        except URLError as err:
            raise ThreeScaleConnectionError("Connection error %s: "
                                        "%s" % (auth_url, err))
        except Exception as err:
            # handle all other exceptions
            raise ThreeScaleException("Unknown error %s: "
                                        "%s" % (auth_url, err))

    def build_auth_response(self):
        """
        Store the xml response from authorize GET api in a Python
        object, ThreeScaleAuthorizeResponse. The values in xml output
        can be retrived using the class methods.

        @returns ThreeScaleAuthorizeResponse object.
        @throws ThreeScaleException error, if xml output received from
        the server is not valid.
        """

        xml = None
        resp = ThreeScaleAuthorizeResponse()

        try:
            xml = etree.fromstring(self.auth_xml)
        except Exception as err:
            raise ThreeScaleException("Invalid xml %s" % err)

        status = xml.xpath('/status')
        if status:
            resp.set_plan(xml.xpath('/status/plan')[0].text)
            reports = xml.xpath('/status/usage_reports/usage_report')
            for report in reports:
                resp.add_usage_report(report)

        if not self.authorized:
            if self.error_code == 409 and status:
                resp.set_reason(xml.xpath('/status/reason')[0].text)
            elif self.error_code == 403 or self.error_code == 404:
                resp.set_reason(xml.xpath('/error')[0].text)
        return resp


class ThreeScaleAuthorizeUserKey(ThreeScale):
    """ThreeScaleAuthorizeUserKey(): The derived class for ThreeScale. It is
    main class to invoke authorize GET API."""

    def validate(self):
        """validate the arguments. If any of following parameters is
        missing, exit from the script.
        - user key
        - provider key

        @throws ThreeScaleException error, if any of the credentials are
        invalid.
        """
        err = []
        if not self.user_key:
            err.append("User key not defined")

        if len(err):
            raise ThreeScaleException(': '.join(err))


    def authorize(self, timeout = 10, usage = { 'hits': 1 }, other_params = {}):
        """authorize() -- invoke authorize GET request.
        - usage passes the usage of each metric of your API.
        - other_params passes other parameters to the authrep call, e.g.
          service_id, user_id, a.s.o.

        The authorize response is stored in a class variable.

        returns True, if authorization is successful.
        @throws ThreeScaleServerError error, if invalid response is
        received.
        @throws ThreeScaleConnectionError error, if connection can not be
        established.
        @throws ThreeScaleException error, if any other unknown error is
        occurred while receiving response for authorize GET api.
        """
        self.authorized = False
        self.auth_xml = None

        self.validate()
        auth_url = self.get_auth_url()
        query_str = self.get_query_string(other_params, usage)

        query_url = "%s?%s" % (auth_url, query_str)
        try:
            req = Request(query_url)
            self.add_version_header(req)
            resp = urlopen(req, timeout=timeout).read()
            self.authorized = True
            self.auth_xml = resp
            return True
        except HTTPError as err:
            if err.code in [403, 404, 409]:
               self.authorized = False
               self.error_code  = err.code
               self.auth_xml = err.read()
               return False

            raise ThreeScaleServerError("Invalid response for url "
                                        "%s: %s" % (auth_url, err))
        except URLError as err:
            raise ThreeScaleConnectionError("Connection error %s: "
                                        "%s" % (auth_url, err))
        except Exception as err:
            # handle all other exceptions
            raise ThreeScaleException("Unknown error %s: "
                                        "%s" % (auth_url, err))

    def build_auth_response(self):
        """
        Store the xml response from authorize GET api in a Python
        object, ThreeScaleAuthorizeResponse. The values in xml output
        can be retrived using the class methods.

        @returns ThreeScaleAuthorizeResponse object.
        @throws ThreeScaleException error, if xml output received from
        the server is not valid.
        """

        xml = None
        resp = ThreeScaleAuthorizeResponse()
        try:
            xml = etree.fromstring(self.auth_xml)
        except Exception as err:
            raise ThreeScaleException("Invalid xml %s" % err)

        status = xml.xpath('/status')
        if status:
            resp.set_plan(xml.xpath('/status/plan')[0].text)
            reports = xml.xpath('/status/usage_reports/usage_report')
            for report in reports:
                resp.add_usage_report(report)

        if not self.authorized:
            if self.error_code == 409 and status:
                resp.set_reason(xml.xpath('/status/reason')[0].text)
            elif self.error_code == 403 or self.error_code == 404:
                resp.set_reason(xml.xpath('/error')[0].text)
        return resp

class ThreeScaleAuthorizeResponse():
    """The derived class for ThreeScale() class. The object constitutes
    the xml data retrived from authorize GET api."""
    def __init__(self):
        self.reason = None
        self.plan = None
        self.usage_reports = []

    def set_plan(self, plan):
        self.plan = plan

    def get_plan(self):
        return self.plan

    def set_reason(self, reason):
        self.reason = reason

    def get_reason(self):
        return self.reason

    def add_usage_report(self, xml):
        """
        Create the ThreeScaleAuthorizeResponseUsageReport object for
        each usage report.
        """
        report = ThreeScaleAuthorizeResponseUsageReport()
        report.set_metric(xml.xpath('@metric')[0])
        period = xml.xpath('@period')[0]
        report.set_period(period)
        if period != "eternity":
            start = xml.xpath('period_start')[0].text
            end = xml.xpath('period_end')[0].text
            report.set_interval(start, end)
        report.set_max_value(xml.xpath('max_value')[0].text)
        report.set_current_value(xml.xpath(\
                                'current_value')[0].text)
        self.usage_reports.append(report)

    def get_usage_reports(self):
        """get all usage reports returned by the authorize GET api."""
        return self.usage_reports


class ThreeScaleAuthorizeResponseUsageReport():
    """Object to store all information related to the usage report."""
    def __init__(self):
        self.metric = None
        self.period = None
        self.start = None
        self.end = None
        self.max_value = None
        self.current_value = None
        self.start_period = None
        self.end_period = None

    def set_metric(self, metric):
        self.metric = metric

    def set_period(self, period):
        self.period = period

    def set_interval(self, start, end):
        self.start_period = start
        self.end_period = end

    def set_end_period(self, end_period):
        self.end_period = end_period

    def set_max_value(self, max_value):
        self.max_value = max_value

    def set_current_value(self, current_value):
        self.current_value = current_value

    def get_metric(self):
        return self.metric

    def get_period(self):
        return self.period

    def get_start_period(self):
        return self.start_period

    def get_end_period(self):
        return self.end_period

    def get_max_value(self):
        return self.max_value

    def get_current_value(self):
        return self.current_value


class ThreeScaleReport(ThreeScale):
    """ThreeScaleReport()
    The derived class for ThreeScale() base class, for making report
    POST request.
    """

    def build_post_data(self, transactions):
        if self.service_token:
            body_params = "service_token=%s" % (self.service_token)
        else:
            body_params = "provider_key=%s" % (self.provider_key)
        if self.service_id:
            body_params = "%s&service_id=%s" % (body_params, self.service_id)
        body_params = "%s&%s" % (body_params, self.encode_transactions(transactions))
        return body_params.encode(ThreeScale.ENCODING)

    def encode_transactions(self, transactions):
        """
        @throws ThreeScaleException error, if transaction is invalid.
        """
        encoded = ''
        i = 0

        if not isinstance(transactions, (tuple, list)):
            raise ThreeScaleException("Invalid transaction type")

        for trans in transactions:
            prefix = "&transactions[%d]" % (i)
            encoded += self.encode_recursive(prefix, trans)
            i += 1

        return encoded

    def encode_recursive(self, prefix, trans):
        """encode every value in transactions
        @throws ThreeScaleException error, if the timestamp specified in
        transaction is invalid.
        """
        new_value = ""
        for key in trans.keys():
            if key == 'usage': # usage is list
                    new_prefix=("%s[usage]" % (prefix))
                    new_value += self.encode_recursive(new_prefix, trans[key])
            elif key == 'timestamp': # specially encode the timestamp
                ts = trans[key]
                try:
                    new_value += "%s[%s]=%s" % (prefix, key, quote(str(time.strftime('%Y-%m-%d %H:%M:%S %z', ts))))
                except Exception:
                    raise ThreeScaleException("Invalid timestamp "
                                              "'%s' specified in "
                                              "transaction" % ts)
            else:
                new_value += ("%s[%s]=%s" % (prefix, key, quote(str(trans[key]))))

        return new_value

    def report(self, transactions, timeout = 10):
        """send the report POST request.

        @returns True, if request is sent successfully.
        @throws ThreeScaleServerError error, if invalid response is
        received.
        @throws ThreeScaleConnectionError error, if connection can not be
        established.
        @throws ThreeScaleException error, if any other unknown error is
        occurred while receiving response for report POST api.
        """

        report_url = self.get_report_url()
        data = self.build_post_data(transactions)

        try:
            req = Request(report_url, data)
            self.add_version_header(req)
            urlopen(req, timeout=timeout)
            return True
        except HTTPError as err:
            raise ThreeScaleServerError("Invalid response for url "
                                        "%s: %s" % (report_url, err))
            return False
        except URLError as err:
            raise ThreeScaleConnectionError("Connection error %s: "
                                        "%s" % (report_url, err))
            return False
        except Exception as err:
            # handle all other exceptions
            raise ThreeScaleException("Unknown error %s: "
                                        "%s" % (report_url, err))
            return False

class ThreeScaleException(Exception):
    """main exception class. raise this exception for all other errors"""
    pass

class ThreeScaleServerError(ThreeScaleException):
    """raise exception if there are any exception during server
    interaction"""
    pass

class ThreeScaleConnectionError(ThreeScaleException):
    """raise exception if server connection can not be establised"""
    pass
