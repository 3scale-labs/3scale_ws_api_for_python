# Client for 3scale web service management system API [![Build Status](https://secure.travis-ci.org/3scale/3scale_ws_api_for_python.png?branch=master)](http://travis-ci.org/3scale/3scale_ws_api_for_python)
3scale integration plugin for Python applications. 3scale is an API Infrastructure service which handles API Keys, Rate Limiting, Analytics, Billing Payments and Developer Management. Includes a configurable API dashboard and developer portal CMS. More product stuff at http://www.3scale.net/, support information at http://support.3scale.net/.

# Synopsis
This plugin supports the 3 main calls to the 3scale backend:

- authrep grants access to your API and reports the traffic on it in one call.
- authorize grants access to your API.
- report reports traffic on your API.

3scale supports 3 authentication modes: App Id, User Key and OAuth. The first two are similar on their calls to the backend, they support authrep. OAuth differs in its usage two calls are required: first authorize then report.

# Installation:

Using Pip:  
```Shell
pip install ThreeScalePY
```

Standard distutils installation:  
download, unpack 3scale_ws_api_for_python, and from 3scale_ws_api_for_python directory run  

```Shell
python setup.py install
```

or you may put ThreeScalePY.py inside the same directory as your program.

## Dependencies

**libxml2** is required, if you are unable to install (as in Google AppEngine), please use the ElementTree branch.

You can get the libxml2 bindings for Python from: ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.21.tar.gz  

The easiest way to install it is using pip:
```Shell
pip install -r requirements.txt
```

# Usage:

All the calls are made through HTTPS by default.
Should you want to use plain HTTP, you need only change the *protocol* class variable in ThreeScalePY.py.

## AuthRep, the recommended approach:

Doing an authrep for the AppId or UserKey authenthication patterns is as follows:

```Python
import ThreeScalePY
authrep = ThreeScalePY.ThreeScaleAuthRep(provider_key)
if authrep.authrep(app_id, app_key):
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())
```

if you are using the UserKey authentication pattern do this:

```Python
import ThreeScalePY
authrep = ThreeScalePY.ThreeScaleAuthRepUserKey(provider_key)
if authrep.authrep(user_key):
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())
```

These examples are doing a default authrep call to the metric 'hits' with usage 1, you can pass several metrics by doing:

```Python
authrep.authrep({"hits": 10, "other_metric": 12, ...}):
```

check the implementation and [authrep's active docs](https://support.3scale.net/reference/activedocs#operation/26) for more parameters.

## Authorize transactions:

```Python
ThreeScalePY.ThreeScaleAuthorize("provider key").authorize("app id", "app key")

ThreeScalePY.ThreeScaleAuthorizeUserKey("provider key").authorize("user key")
```

## Report transactions:

You can report up to 1000 transactions in a single request. In case you have multiple services, transactions to different services have to be reported on different calls.

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"app_id":"app id 1", "usage":{"hits":1, "other_metric":5}},
{"app_id":"app id 2", "usage":{"hits":1, "other_metric":5}},
{"app_id":"app id 3", "usage":{"hits":1, "other_metric":5}}
])
```
OR

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"user_key":"user key 1", "usage":{"hits":1, "other_metric":5, "timestamp"}},
{"user_key":"user key 2", "usage":{"hits":1, "other_metric":5}},
{"user_key":"user key 3", "usage":{"hits":1, "other_metric":5}}
])
```

## Using Authorize and Report together
You can use this approach for all authentication patterns. For OAuth this is the only possible approach.
Note that the report call to 3scale backend is asynchronous, so the metrics for your API will not be updated instantly.

```Python
authorizer = ThreeScalePY.ThreeScaleAuthorize(provider_key)
reporter = ThreeScalePY.ThreeScaleReport(provider_key)

if authorizer.authorize(app_id, app_key):
    #building a sample transaction report
    t1 = {}
    t1_usage = {}
    t1_usage['hits'] = 5
    t1['app_id'] = app_id
    t1['usage'] = t1_usage
    t1['timestamp'] = time.gmtime(time.time())
    transactions= [t1]
    if reporter.report(transactions):
        # all was ok, call was authorized and report was succesful. Proceed normally.
    else:
        # reporting unsuccesful
else:
    # authorization unsuccesful. Fetch error description.
    sys.stdout.write(" reason = %s \n" % authorizer.build_response().get_reason())
```


# To test:

To test the plugin with your real data:
- set your app_id, app_key and provider_key in tests/tests.py
- run **python tests/tests.py**

