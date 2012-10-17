# Client for 3scale web service management system API [![Build Status](https://secure.travis-ci.org/3scale/3scale_ws_api_for_python.png?branch=master)](http://travis-ci.org/3scale/3scale_ws_api_for_python)
3scale integration plugin for Python applications. 3scale is an API Infrastructure service which handles API Keys, Rate Limiting, Analytics, Billing Payments and Developer Management. Includes a configurable API dashboard and developer portal CMS. More product stuff at http://www.3scale.net/, support information at http://support.3scale.net/.

# Installation:

Standard distutils installation: unpack ThreeScale-2.0.tar.gz, and from ThreeScale-2.0 directory run

```Shell
sudo python setup.py install
```

or you may put ThreeScalePY.py to the same directory as your program

libxml2 is required, if you are unable to install (as in Google AppEngine), please use the ElementTree branch.

# Usage:

## AuthRep, the recommended approach:

Doing an authrep for the AppId or OAuth authenthication patterns is as follows:

```Python
import ThreeScalePY
authrep = ThreeScalePY.ThreeScaleAuthRep(provider_key, app_id, app_key)
if authrep.authrep():
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())
```

if you are using the UserKey auth pattern do this:

```Python
import ThreeScalePY
authrep = ThreeScalePY.ThreeScaleAuthRepUserKey(provider_key, user_key)
if authrep.authrep():
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())
```

These examples are doing a default authrep call to the metric 'hits' with usage 1, you can pass several metrics by doing:

```Python
authrep.authrep({"hits": 10, "metric1": 12, ...}):
```

check the implementation and [authrep's active docs](https://support.3scale.net/reference/activedocs#operation/26) for more parameters.

## Authorize transactions:

```Python
ThreeScalePY.ThreeScaleAuthorize("provider key", "app id", "app key").authorize()

ThreeScalePY.ThreeScaleAuthorizeUserKey("provider key", None, None, "user key").authorize()
```

## Report transactions:

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"app_id":"app id", "usage":{"hits":1, "max_value":5}}]
```
OR

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"user_key":"user key", "usage":{"hits":1, "max_value":5}}]
```
