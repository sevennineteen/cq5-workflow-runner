# cq5-workflow-runner

## Overview

This script may be used to initiate CQ5 workflows against multiple CRX resources, as returned in a query result set. It functions essentially as a wrapper to CQ's REST APIs for [QueryBuilder](http://dev.day.com/docs/en/cq/current/dam/customizing_and_extendingcq5dam/query_builder.html) and [workflows](http://dev.day.com/docs/en/cq/current/developing/developing_workflows/workflows_rest_api.html), respectively.

## Usage

Customize **INSTANCE-SPECIFIC CONSTANTS** as follows:

* `CQ_SERVER`: CQ server address
* `USERNAME`: CQ username
* `PASSWORD`: CQ password

* `SEARCH_ROOT_PATH`: branch/folder within which to execute your query
* `WORKFLOW_MODELS`: list of paths to the workflow models to be run across query result set
* `QUERY_PARAMS`: dictionary of parameters specifying criteria for inclusion

In short, `SEARCH_ROOT_PATH` and `QUERY_PARAMS` define the *scope* of objects to be processed, and `WORKFLOW_MODEL` dictates what processing will happen.

After updating the constants appropriately, execute the script from a Python shell. The provided query will be executed, and a new workflow instance will be started for each resource in the result set.

    python cq5-workflow-runner.py

## Caveats

1. While API calls are synchronous and single-threaded, a new workflow request will be sent once CQ has acknowleged that the preceding one has been created, *not* that it has been finished, so a backlog is possible. Users are advised to monitor job queues in the **Instances** tab of CQ's Workflow console to avoid overloading the server.

2. You may encounter unmet dependencies for Python modules not included in the standard library, such as `simplejson`. Review the import statements at the top of each script and install necessary modules using `easy_install` or `pip`.