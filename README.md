# Client for 3scale web service management system API [![Build Status](https://secure.travis-ci.org/3scale/3scale_ws_api_for_python.png?branch=master)](http://travis-ci.org/3scale/3scale_ws_api_for_python)
3scale integration plugin for Python applications. 3scale is an API Infrastructure service which handles API Keys, Rate Limiting, Analytics, Billing Payments and Developer Management. Includes a configurable API dashboard and developer portal CMS. More product stuff at http://www.3scale.net/, support information at http://support.3scale.net/.

# Synopsis
This plugin supports the 3 main calls to the 3scale Service Management API:

- `authrep` grants access to your API and reports the traffic on it in one call.
- `authorize` grants access to your API.
- `report` reports traffic on your API.

3scale supports 3 authentication modes: App Id, User Key and OAuth. The first two are similar on their calls to the Service Management API, they support authrep. OAuth differs in its usage two calls are required: first authorize then report.

Check the [3scale APIs ActiveDocs](https://support.3scale.net/docs/3scale-apis-activedocs) to learn more about the supported parameters.

# Installation:

## Using Pip:  
```shell
pip install ThreeScalePY
```
## Standard setuptools installation:
- clone or download the repository
- unpack to `3scale_ws_api_for_python`
- from `3scale_ws_api_for_python` run:

```shell
python setup.py install
```

or you may put `ThreeScalePY.py` inside the same directory as your program.

## Dependencies

**lxml** is required.

You can get the `lxml` bindings for Python from: https://github.com/lxml/lxml/releases

The easiest way to install it is using pip:
```shell
pip install -r requirements.txt
```

# Usage:

## Credentials

You will need to send the valid credentials to make calls to the 3scale Service Management API. The preferred way is to use the Service Tokens, which are unique for each service. You can find the Service Tokens in the Personal Settings > Tokens page of your 3scale admin portal. You can also use the Provider API key in the current version of the plugin, however it may be deprecated in future releases.
You can read more about the different API keys available to access the 3scale APIs from the [terminology page](https://support.3scale.net/docs/terminology) of the 3scale support portal.

Since November 2016 it is also required to provide the Service ID (`service_id`) parameter when making calls to the 3scale Service Management API.


## AuthRep, the recommended approach:

Doing an authrep for the App Id authenthication pattern is as follows:

```Python
import sys
import ThreeScalePY
authrep = ThreeScalePY.ThreeScaleAuthRep(app_id = 'your_app_id', app_key = 'your_app_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
if authrep.authrep():
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % authrep.build_response().get_reason())
```

If you are using the Provider API key, use the following to initialize `authrep` instead:

```Python
authrep = ThreeScalePY.ThreeScaleAuthRep('your_provider_key', 'your_app_id', 'your_app_key')
```

If you are using the User Key authentication pattern use the following:

```Python
authrep = ThreeScalePY.ThreeScaleAuthRepUserKey(user_key = 'your_user_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
```

or, with the Provider API key:

```Python
authrep = ThreeScalePY.ThreeScaleAuthRepUserKey('your_provider_key', 'your_user_key', service_id = 'your_service_id')
```

These examples are doing a default authrep call to the metric `hits` with usage 1, you can pass several metrics by doing:

```Python
authrep.authrep({'hits': 10, 'custom_metric': 12, ... }):
```

## Authorize transactions:

To make an authorize call:

```Python
import sys
import ThreeScalePY
auth = ThreeScalePY.ThreeScaleAuthorize(app_id = 'your_app_id', app_key = 'your_app_key', 
                          service_id = 'your_service_id', service_token = 'your_service_token')
if auth.authorize():
    # all was ok, proceed normally
else: # something was wrong
    sys.stdout.write(" reason = %s \n" % auth.build_auth_response().get_reason())
```

Using the Provider API key:

```Python
ThreeScalePY.ThreeScaleAuthorize('your_provider_key', 'your_app_id', 'your_app_key', service_id = 'your_service_id').authorize()
```

For the User Key authentication mode:

```Python
ThreeScalePY.ThreeScaleAuthorizeUserKey(user_key = 'your_user_key', service_id = 'your_service_id',
                          service_token = 'your_service_token').authorize()
```

or with the Provider API key:

```Python
ThreeScalePY.ThreeScaleAuthorizeUserKey('your_provider_key', None, None, 'your_user_key', service_id = 'your_service_id').authorize()
```

## Report transactions:

You can report up to 1000 transactions in a single request. In case you have multiple services, transactions to different services have to be reported on different calls.

To make report calls:

```Python
ThreeScalePY.ThreeScaleReport(service_id = 'your_service_id', service_token = 'your_service_token').report([{'app_id':'your_app_id', 'usage':{'hits':1, 'custom_metric':5}}])
```
or

```Python
ThreeScalePY.ThreeScaleReport(service_id = 'your_service_id', service_token = 'your_service_token').report([{'user_key':'your_user_key', 'usage':{'hits':1, 'custom_metric':5}}])
```

Using the Provider API key:

```Python
ThreeScalePY.ThreeScaleReport('your_provider_key', service_id = 'your_service_id').report([{'app_id':'your_app_id', 'usage':{'hits':1, 'custom_metric':5}}])
```
or

```Python
ThreeScalePY.ThreeScaleReport('your_provider_key', service_id = 'your_service_id').report([{'user_key':'your_user_key', 'usage':{'hits':1, 'custom_metric':5}}])
```

## Custom backend for the 3scale Service Management API

The default URI used for the 3scale Service Management API is `https://su1.3scale.net:443`. This value can be changed, which is useful when the plugin is used together with the on-premise version of the Red Hat 3scale API Management Platform.

In order to override the URL, you will need to pass the argument `backend_uri` to the constructor, for example:

```Python
authrep = ThreeScalePY.ThreeScaleAuthRepUserKey(user_key = user_key, service_id = service_id, 
                  service_token = service_token, 
                  backend_uri = 'http://custom-backend.example.com:8080')
```

# Testing

To test the plugin with your real data:

1. set the environment variables:
  - `TEST_3SCALE_APP_ID`
  - `TEST_3SCALE_APP_KEY`
  - `TEST_3SCALE_PROVIDER_KEY`
  - `TEST_3SCALE_SERVICE_ID`
  - `TEST_3SCALE_SERVICE_TOKEN`

2. run:
```shell
python tests/tests.py
```
