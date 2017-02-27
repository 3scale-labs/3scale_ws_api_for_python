# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.6.0]
### Added
- `service_token` is supported along with `provider_key`
- Backend URL is configurable, so the plugin can be used with on-premises 3scale API Management Platform
- `authorize()` method supports `usage` and `other_params` arguments
- Python 3 support
- Adds `X-3scale-User-Agent` header (value format: plugin-python-v{version_number})

### Changed
- `service_id` parameter is required (for accounts created before November 2016 backward compatibility is maintained)
- Fixed bug [#7](https://github.com/3scale/3scale_ws_api_for_python/issues/7)
- Start [semantic versioning](http://semver.org/)
- Use `setuptools` instead of `distutils`