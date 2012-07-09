# 3scale API Management Plugin for Python

3scale is an API Infrastructure service which handles API Keys, Rate Limiting, Analytics, Billing Payments and Developer Management. Includes a configurable API dashboard and developer portal CMS. More product stuff at http://www.3scale.net/, support information at http://support.3scale.net/.

## Installation:

Standard distutils installation - just unpack ThreeScale-2.0.tar.gz, and from ThreeScale-2.0 directory run

    sudo python setup.py install

or you may put ThreeScalePY.py to the same directory as your program. (Note: a Pypi package is planned to be released soon. If you are willing to help with it, please fork and issue a pull request).


## USAGE:

To load the library, use:

    import ThreeScalePY


### Authorize a transaction:

To authorize an application, create either a `ThreeScaleAuthorize` instance:

     auth = ThreeScalePY.ThreeScaleAuthorize("provider key", "app id", "app key").authorize()

or (if you are using user key authentication) a `ThreeScaleAuthorizeUserKey` object:

     auth = ThreeScalePY.ThreeScaleAuthorizeUserKey("provider key", None, None, "user key").authorize()

and call an `authorize()` method on the obtained object:

    if auth.authorize():
      resp = auth.build_auth_response()
    else:
      print "ERROR: Failed to authorize"


### Report a transaction:

Use `ThreeScaleReport` class to report hits like this:

    ThreeScalePY.ThreeScaleReport("provider key").report([{"app_id":"app id", "usage":{"hits":1, "max_value":5}}]

or again with `user_key`

    ThreeScalePY.ThreeScaleReport("provider key").report([{"user_key":"user key", "usage":{"hits":1, "max_value":5}}]
