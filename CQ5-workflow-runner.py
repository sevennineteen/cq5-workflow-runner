"This script initiates CQ workflows against resources returned by the supplied query."

import logging
import simplejson as json
import httplib2
import urllib
import base64
from uuid import uuid4

#----------------------------------------------------------
# INSTANCE-SPECIFIC CONSTANTS // customize before running
CQ_HOSTNAME = 'localhost'
CQ_SERVER = 'http://%s:4502' % CQ_HOSTNAME
USERNAME = 'admin'
PASSWORD = 'admin'

SEARCH_ROOT_PATH = '/content/dam'
WORKFLOW_MODELS = [ '/etc/workflow/models/dam/update_asset',
                    '/etc/workflow/models/dam/dam_set_last_modified'
                    ]
QUERY_PARAMS = {    'path': SEARCH_ROOT_PATH,
                    'type': 'dam:Asset',
                    #'nodename': '*.jpg',
                    'group.p.or': 'true',
                    'group.1_nodename': '*.jpg',
                    'group.2_nodename': '*.gif',
                    'p.limit': '-1'
                    }
#----------------------------------------------------------

# Initialize logging
logging.basicConfig(    filename='workflow-runner-%s.log' % CQ_HOSTNAME,
                        format='%(asctime)s %(levelname)-6s %(message)s',
                        level=logging.INFO,
                        filemode='a'
                        )
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-6s%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

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
    logging.info('Executing query: %s' % url)
    try:
        http = httplib2.Http()
        response = http.request(url, headers=headers)
        if response[0].status != 200:
            raise Exception, 'Unexpected response status (%s)' % response[0].status
        results = json.loads(response[1])
        return [x['path'] for x in results['hits']]
    except Exception, e:
        logging.error('!!! Failed to execute query with URL: %s.' % url)
        logging.error('--> %s' % e.message)

def start_workflow(model, payload, url=WORKFLOW_URL, headers=CQ_AUTH_HEADER):
    "Starts a workflow for the specified payload."
    try:
        http = httplib2.Http()
        data = {    'model': model + '/jcr:content/model',
                    'payload': payload,
                    'payloadType': 'JCR_PATH',
                    'workflowTitle': uuid4().hex
                    }
        headers.update({'Content-type': 'application/x-www-form-urlencoded'})
        response = http.request(url, headers=headers, method='POST', body=urllib.urlencode(data))
        if response[0].status != 201:
            raise Exception, 'Unexpected response status (%s)' % response[0].status
        logging.info('Started workflow %s for %s (%s)' % (model.replace('/etc/workflow/models', ''), payload, data['workflowTitle']))
    except Exception, e:
        logging.error('Failed to start workflow %s for %s.' % (model.replace('/etc/workflow/models', ''), payload))
        logging.error('--> %s' % e.message)
        try:
            logging.error(response[1])
        except:
            pass

logging.info('-' * 150)
resources = execute_query()
logging.info('Query returned %s resources.' % len(resources))
for r in resources:
    print '(%s/%s)' % (resources.index(r) + 1, len(resources))
    map(lambda w: start_workflow(w, r), WORKFLOW_MODELS)
logging.info('-' * 150)