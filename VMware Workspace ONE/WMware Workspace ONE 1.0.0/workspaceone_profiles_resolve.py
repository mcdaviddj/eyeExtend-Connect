"""
Copyright © 2021 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import json
import logging
import urllib.request
from urllib.request import HTTPError


WO_PROTOCOL = "https"
WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_SERVER_ADDRESS = params.get("connect_workspaceone_server_url")
WO_API_KEY = params.get("connect_workspaceone_api_key")


# Proxy support
workspaceone_proxy_enabled = params.get("connect_proxy_enable")
workspaceone_proxy_basic_auth_ip = params.get("connect_proxy_ip")
workspaceone_proxy_port = params.get("connect_proxy_port")
workspaceone_proxy_username = params.get("connect_proxy_username")
workspaceone_proxy_password = params.get("connect_proxy_password")
opener = workspaceone_proxy_support.handle_proxy_configuration(workspaceone_proxy_enabled,
							workspaceone_proxy_basic_auth_ip,
							workspaceone_proxy_port,
							workspaceone_proxy_username,
							workspaceone_proxy_password, ssl_context)


# construct 'profile resolve' response to CounterACT
response = {}
	
wo_to_ct_subfields_composite_map = {
	"Name": "connect_workspaceone_profile_name",
	"AssignmentType": "connect_workspaceone_profile_assignment_type",
	"Status": "connect_workspaceone_profile_status"
}


device_id = params.get("connect_workspaceone_deviceID")
if device_id:

	profl_url = WO_PROTOCOL + "://" + WO_SERVER_ADDRESS + "/api/mdm/devices/" + device_id + "/profiles"
	logging.debug("WO profl Resolve URL " + profl_url)

	headers = workspaceone_authentication_and_epoch.get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY)

	try:
		logging.debug("Starting profiles resolve...")

		prop_request = urllib.request.Request(profl_url, headers=headers)
		prop_response_handle = opener.open(prop_request)

		prop_response = prop_response_handle.read().decode("utf-8")
		prop_response_json = json.loads(prop_response)
		logging.debug("WO profile Resolve response: " + str(prop_response))

		# handle empty response
		if not prop_response_json.get("Total"):
			logging.debug("No profiles for device_id: " + device_id)
			response["succeeded"] = False
			response["error"] = "Workspace ONE Host does not have any profls installed. WO Device ID= {}".format(device_id)
		else:
			profls = prop_response_json.get("DeviceProfiles")

			# list of profiles sent to Forescout
			profls_list = []
			
			properties = {}

			profl_count = prop_response_json.get("Total")
			for i in range(profl_count):
				profl = profls[i]
				profile =  {}
				for prop_key, prop_val in profl.items():
					if prop_key in wo_to_ct_subfields_composite_map.keys():
						subfield_name = wo_to_ct_subfields_composite_map[prop_key]
						profile[subfield_name] = str(prop_val)
				profls_list.append(profile)
			
			properties["connect_workspaceone_profiles"] = profls_list
			response["properties"] = properties
			logging.debug("Profiles on Device ID {}: {}".format(device_id, response))

		logging.debug("profile inventory resolve completed")
	except HTTPError as e:
		response["succeeded"] = False
		response["error"] = "Could not connect to WorkspaceONE. HTTP Response code: {}".format(e.code)
	except Exception as e:
		response["succeeded"] = False
		response["error"] = "Could not connect to WorkspaceONE. {}".format(str(e))
else:
	response["succeeded"] = False
	response["error"] = "Device identifier field is empty."
