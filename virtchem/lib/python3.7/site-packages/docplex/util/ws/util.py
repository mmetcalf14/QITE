# --------------------------------------------------------------------------
# Source file provided under Apache License, Version 2.0, January 2004,
# http://www.apache.org/licenses/
# (c) Copyright IBM Corp. 2019
# --------------------------------------------------------------------------

import json
import uuid
try:
    from IPython.display import Javascript, HTML, display
except ImportError:
    Javascript = None

CATEGORY = "Decision Optimization"
START_SOLVE_EVENT = "Solve in Notebook"
END_SOLVE_EVENT = "End solve in Notebook"

def generate_payload(category, event, details=None, hw_spec=None):
    payload = {'action' : event,
               'model': {'type': 'python'},
               'category': category }
    if details:
        payload['details'] = details
    if hw_spec:
        payload['hardware_spec'] = hw_spec
    return json.dumps(payload, indent=3)

def generate_js(category, event, details=None):   
    template ='''
        if (parent && parent.analytics)
            parent.analytics.track("{category}: {event}",
                                    {payload})
    '''.format(payload=generate_payload(category, event, details),
               category=category, event=event)
    return template


class Tracker(object):    
    # Amplitude tracker to get instrumentation when running on WS
    def notify_ws(self, event, details=None):
        '''
        PRODUCT_TITLE = "Watson Studio";
    
        CATEGORIES = {
            "DECISION_OPTIMIZATION": "Decision Optimization"
        };
        
        EVENTS = {
            "CREATE_MODEL": "Create Model",
            "RUN_MODEL": "Run Model",
            "VIEW_MODEL": "View Model"
        };
        '''
        if Javascript:
            js = generate_js(CATEGORY, event, details)
            uid = str(uuid.uuid4())
            display(Javascript(js), display_id=uid)
            display(HTML('<div></div>'), update=True, display_id=uid)

            