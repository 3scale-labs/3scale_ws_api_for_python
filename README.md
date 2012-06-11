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

In short:
```Python
import ThreeScalePY
```

# USAGE:

# Authorize a transaction:

```Python
ThreeScalePY.ThreeScaleAuthorize("provider key", "app id", "app key").authorize()

ThreeScalePY.ThreeScaleAuthorizeUserKey("provider key", None, None, "user key").authorize()
```

# Report a transaction:

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"app_id":"app id", "usage":{"hits":1, "max_value":5}}]
```
OR

```Python
ThreeScalePY.ThreeScaleReport("provider key").report([{"user_key":"user key", "usage":{"hits":1, "max_value":5}}]
```
