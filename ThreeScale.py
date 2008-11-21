"""This module provides interface to 3scale backend server.
 
 == Basic usage instructions
 
 First import 3scale module:
 
    import ThreeScale
 
 Next, create new interface object with 3scale backed hostname and Your
 private provider key:
 
    interface = ThreeScale.Interface("http://3scale.net", "a3b034...")
 
 Then for each request to Your service:
 
 1. Start the transaction with user key and (optionaly) predicted resource
 usage (in this example it is: 1 hit and 42000 kilobytes of storage space),
 
     transaction = interface.start(user_key, hits = 1, storage = 42000)
 
 This will return transaction data (if succesful). It is a hash containing
 these fields:
 
  'id': transaction id necessary for confirmation of cancelation of
  transaction (see following steps).
 
  'provider_verification_key': key You should send back to user so he/she
  can verify the authenticity of the response.
 
  'contract_name': name of contract the user is signed for. This can be used
  to send different response according to contract type, if that is desired.
 
 2. Process the request.
 
 3a. If the processing was succesful:
 Call confirm:
 
     interface.confirm(transaction['id'])
 
 Or call it with actual resource usage, if it differs from predicted one:
 
     interface.confirm(transaction['id'], hits = 1, storage = 40500)
 
 3b. If there was some error, call cancel:
 
     interface.cancel(transaction_id)
 
 4. Send response back to the user with transaction['provider_public_key']
 embeded.
"""

import httplib
import xml.dom.minidom
from urlparse import urlparse
from urllib import quote_plus, urlencode

class Error(StandardError):
	pass

class UserError(Error):
	"""Base class for errors caused by user."""
	pass

class ContractNotActive(UserError):
	"""Error raised when user's contract instance is not active."""
	pass

class LimitsExceeded(UserError):
	"""Error raised when usage limits specified by user's contract are exceeded."""
	pass

class UserKeyInvalid(UserError):
	"""Error raised when user_id is invalid."""
	pass
  
class ProviderError(Error):
	"""Base class for errors caused by provider."""
	pass

class MetricInvalid(ProviderError):
	"""Error raised when some metric names are invalid."""
	pass

class ProviderKeyInvalid(ProviderError):
	"""Error raised when provider authentication key is invalid."""
	pass

class TransactionNotFound(ProviderError):
	"""Error raised when transaction id does not correspond to existing transaction."""
	pass

class SystemError(Error):
	"""Base class for errors caused by 3scale backend system."""
	pass
class UnknownError(Error):
	pass

class Interface:
	"""This class provides interface to 3scale backend server.
	 
	 == Basic usage instructions
	 
	 First import 3scale module:
	 
	    import ThreeScale
	 
	 Next, create new interface object with 3scale backed hostname and Your
	 private provider key:
	 
	    interface = ThreeScale.Interface("http://3scale.net", "a3b034...")
	 
	 Then for each request to Your service:
	 
	 1. Start the transaction with user key and (optionaly) predicted resource
	 usage (in this example it is: 1 hit and 42000 kilobytes of storage space),
	 
	     transaction = interface.start(user_key, hits = 1, storage = 42000)
	 
	 This will return transaction data (if succesful). It is a hash containing
	 these fields:
	 
	  'id': transaction id necessary for confirmation of cancelation of
	  transaction (see following steps).
	 
	  'provider_verification_key': key You should send back to user so he/she
	  can verify the authenticity of the response.
	 
	  'contract_name': name of contract the user is signed for. This can be used
	  to send different response according to contract type, if that is desired.
	 
	 2. Process the request.
	 
	 3a. If the processing was succesful:
	 Call confirm:
	 
	     interface.confirm(transaction['id'])
	 
	 Or call it with actual resource usage, if it differs from predicted one:
	 
	     interface.confirm(transaction['id'], hits = 1, storage = 40500)
	 
	 3b. If there was some error, call cancel:
	 
	     interface.cancel(transaction_id)
	 
	 4. Send response back to the user with transaction['provider_public_key']
	 embeded.
	"""

	# URI prefix of 3scale server ('http://beta.3scale.net')
	#uri_prefix
	# Hostname of 3scale server ('beta.3scale.net').
	#host
	# Protocol of 3scale server ('http')
	#proto
	# Path in 3scale server ('')
	#path

	# Key that uniquely identifies the provider. This key is known only to the
	# provider and to 3scale.
	#provider_private_key

	def __init__(self, host = None, provider_private_key = None):
		"""Create a 3scale interface instance.
		
		 == Arguments
		 * host:                 Hostname of 3scale backend server.
		 * provider_private_key: Unique key that identifies this provider.
		"""
		self.uri_prefix = host
		addr = urlparse(self.uri_prefix)
		self.proto = addr[0].lower()
		self.host = addr[1]
		self.path = addr[2]
		self.provider_private_key = self.prepare_key(provider_private_key)

	def start(self, user_key, **usage):
		"""Start a transaction (service request). This can be used also to send
		 prediction of how much resouces will be spend by this request to 3scale
		 backend server.
		
		 == Arguments
		 * user_key:    Key that uniquely identifies an user of the service.
		 * usage:       A hash of that contains metric names and to them
		                associated amounts of resources used. For example, if this
		                request is going to take 10MB of storage space, then this
		                parameter could contain {'storage' => 10}. The values may
		                be only approximate or they can be missing altogether. In
		                these cases, the real values should be reported using
		                method confirm.
		
		 == Return values
		 A hash containing there keys:
		 * 'id':    Transaction id. This is required for confirmation/cancellation
		          of the transaction later.
		 * 'provider_verification_key':    This key should be sent back to the user
		                                 so he/she can use it to verify the
		                                 authenticity of the provider.
		 * 'contract_name':    This is name of the contract the user is singed for.
		                     This information can be used to serve different
		                     responses according to contract types,
		                     if that is desirable.
		
		 == Exceptions
		
		"""
		params = {
			'user_key' : self.prepare_key(user_key),
			'provider_key' : self.provider_private_key
		}
		params.update(self.encode_params(usage, 'usage'))
		response = self.__process_request("POST", "/transactions.xml", params)

		if 200 <= response.status < 400:
			element = xml.dom.minidom.parseString(response.body).getElementsByTagName('transaction')[0]
			memo = {}
			for key in ['id', 'provider_verification_key', 'contract_name']:
				e = element.getElementsByTagName(key)
				if e != []:
					memo[key] = e[0].firstChild.toxml()
			return memo
		else:
			self.handle_error(response.body)

	def __process_request(self, method, path, params):
		"""helper function"""
		if self.proto == "https":
			conn = httplib.HTTPSConnection(self.host)		
		else:
			#try to make http connection by default
			conn = httplib.HTTPConnection(self.host)
		conn.request(method, "%s%s" % (self.path, path),
			urlencode(params),
		#	"&".join(map(lambda p: "%s=%s" % tuple(map(lambda v: quote_plus(v, "[]/"), p)), params.items())),
			{ 'Content-Type' : 'application/x-www-form-urlencoded'} )
		response = conn.getresponse()
		# add body field to response object
		response.body = response.read()
		conn.close()
		return response

	#
	# Confirm previously started transaction. The transaction and the user -- if defined -- will be recorded into
	# the 3scale system. Both parties will be able to access these logs.
	# 
	def confirm(self, transaction_id, **usage):
		"""Confirm previously started transaction."""
		params = {
			'provider_key' : self.provider_private_key
		}
		params.update(self.encode_params(usage, 'usage'))
		response = self.__process_request("POST",
			"/transactions/%s/confirm.xml" % quote_plus(str(transaction_id)),
			params)

		if 200 <= response.status < 400:
			return True
		else:
			self.handle_error(response.body)

	#
	# Cancel previously started transaction
	#
	def cancel(self, transaction_id):
		"""Cancel previously started transaction."""
		response = self.__process_request("DELETE",
			"/transactions/%s.xml" % quote_plus(str(transaction_id)),
			{'provider_key' : self.provider_private_key})

		if 200 <= response.status < 400:
			return True
		else:
			self.handle_error(response.body)


	KEY_PREFIX = '3scale-'

	def is_system_key(self, key):
		"""Check if key is for 3scale backend system."""
		# Key should start with prefix
		return key.find(self.KEY_PREFIX) == 0


	def encode_params(self, params, prefix):
		"""Encode hash into form suitable for sending it as params of HTTP request."""
		memo = {}
		for key, value in params.items():
			memo["%s[%s]" % (prefix, key)] = str(value)
		return memo


	def prepare_key(self, key):
		if self.is_system_key(key):
			return key[len(self.KEY_PREFIX):]
		else:
			return key

	CODES_TO_EXCEPTIONS = {
		'user.exceeded_limits' : LimitsExceeded,
		'user.invalid_key' : UserKeyInvalid,
		'user.inactive_contract' : ContractNotActive,
		'provider.invalid_key' : ProviderKeyInvalid,
		'provider.invalid_metric' : MetricInvalid,
		'provider.invalid_transaction_id' : TransactionNotFound
	}

	def handle_error(self, response):
		try:
			element = xml.dom.minidom.parseString(response).getElementsByTagName('error')
			raise self.CODES_TO_EXCEPTIONS[element[0].getAttribute('id')]
		# bad xml response
		except xml.parsers.expat.ExpatError:
			raise UnknownError
		# error element not found in response
		except IndexError:
			raise UnknownError
		# error is not found in CODES_TO_EXCEPTIONS
		except KeyError:
			raise UnknownError



