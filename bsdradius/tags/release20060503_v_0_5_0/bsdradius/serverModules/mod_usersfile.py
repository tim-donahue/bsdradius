## BSDRadius is released under BSD license.
## Copyright (c) 2006, DATA TECH LABS
## All rights reserved. 
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## * Redistributions of source code must retain the above copyright notice,
##   this list of conditions and the following disclaimer. 
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution. 
## * Neither the name of the DATA TECH LABS nor the names of its contributors
##   may be used to endorse or promote products derived from this software without
##   specific prior written permission. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
BSDRadius module for static users file access
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20060503_v_0_5_0/bsdradius/serverModules/mod_usersfile.py $
# Author:		$Author: valts $
# File version:	$Revision: 209 $
# Last changes:	$Date: 2006-05-02 17:33:15 +0300 (Ot, 02 Mai 2006) $


import exceptions
# you can use functions defined in logger module to use BSD Radius's
# logger system.
from bsdradius.logger import *


class ModusersfileError(exceptions.Exception):
	pass



def authorization(received, check, reply):
	"""Find user in parsed users file
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
	"""	
	
	username = received.get('User-Name', [None])[0]
	password = received.get('User-Password', [None])[0]
	if username == None or password == None:
		raise ModusersfileError, 'Attributes "User-Name" and "User-Password" must be present in request data'
	
	# search user by name
	acctData = config.get(username, {})
	if acctData:
		debug ('Account (%s) found' % acctData.get('description', ''))
	else:
		debug ('User not found')
		# Return true even if account not found. Leave chance for other modules to
		# find the user.
		return True

	# password must be present in config file
	if 'password' not in acctData:
		raise ModusersfileError, '"password" attribute must be present in user configuration file section "%s"' % username
	
	# check if received password is correct
	if password == acctData['password']:
		authType = check.get('Auth-Type', [None])[0]		
		if not authType:
			# just set the auth type to "usersfile" if no previous modules have touched it.
			check['Auth-Type'] = ['usersfile']
		else:
			# pass username and password to module which has set up it's auth type.
			check['User-Name'] = [username]
			check['User-Password'] = [password]
		return True
	# password incorrect - reject user
	else:
		debug ('User password incorrect')
		debug ('  Received: %s' % password)
		debug ('  Expected: %s' % acctData['password'])
		return False



def authentication(received, check, reply):
	"""Tell the server that user is ok
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
	"""
	authType = check.get('Auth-Type', [None])[0]
	if authType == 'usersfile':
		return True
	else:
		return False
