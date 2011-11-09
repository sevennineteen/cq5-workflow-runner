"This script initiates a CQ workflow against resources returned by the supplied query."

import simplejson as json
import httplib2
import urllib
import base64
from uuid import uuid4

#----------------------------------------------------------
# INSTANCE-SPECIFIC CONSTANTS // customize before running
CQ_SERVER = 'http://localhost:4502'
USERNAME = 'admin'
PASSWORD = 'admin'

SEARCH_ROOT_PATH = '/content/dam'
WORKFLOW_MODEL = '/etc/workflow/models/dam/update_asset'
QUERY_PARAMS = {	'path': SEARCH_ROOT_PATH,
					'type': 'dam:Asset',
					'nodename': '*.jpg',
					'p.limit': '-1'
					}
#----------------------------------------------------------

def cq_auth_header(username, password):
    "Converts user credentials to CQ-required request header."
    return {'Authorization': 'Basic %s' % (base64.b64encode('%s:%s' % (username, password)))}

def stringify_params(params):
	"Converts a dictionary of query params into a URL-encoded string."
	return '&'.join(['%s=%s' % (urllib.quote(k), urllib.quote(v)) for k, v in params.items()])

# CQ5 CONSTANTS
WORKFLOW_URL = CQ_SERVER + '/etc/workflow/instances'
QUERYBUILDER_URL = CQ_SERVER + '/bin/querybuilder.json?%s' % stringify_params(QUERY_PARAMS)
CQ_AUTH_HEADER = cq_auth_header(USERNAME, PASSWORD)
    
def execute_query(url=QUERYBUILDER_URL, headers=CQ_AUTH_HEADER):
	"Executes querybuilder query and returns resources in JSON result set."
	try:
		http = httplib2.Http()
		response = http.request(url, headers=headers)
		if response[0].status != 200:
			raise Exception, 'Unexpected response status (%s)' % response[0].status
		results = json.loads(response[1])
		return [x['path'] for x in results['hits']]
	except Exception, e:
		print '!!! Failed to execute query with URL: %s.' % url
		print '--> %s' % e.message

def start_workflow(model, payload, url=WORKFLOW_URL, headers=CQ_AUTH_HEADER):
	"Starts a workflow for the specified payload."
	try:
		http = httplib2.Http()
		data = {	'model': WORKFLOW_MODEL + '/jcr:content/model',
					'payload': payload,
					'payloadType': 'JCR_PATH',
					'workflowTitle': uuid4().hex
					}
		headers.update({'Content-type': 'application/x-www-form-urlencoded'})
		response = http.request(url, headers=headers, method='POST', body=urllib.urlencode(data))
		if response[0].status != 201:
			raise Exception, 'Unexpected response status (%s)' % response[0].status
		print '\tStarted workflow for %s (%s)' % (payload, data['workflowTitle'])
	except Exception, e:
		print '!!! Failed to start workflow for %s.' % payload
		print '--> %s' % e.message

resources = execute_query()
print 'Query returned %s resources.' % len(resources)
for r in resources:
	print '(%s/%s)' % (resources.index(r) + 1, len(resources))
	start_workflow(WORKFLOW_MODEL, r)