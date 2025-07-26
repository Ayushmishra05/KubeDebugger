import subprocess 
import json 

def get_pod_json(resource : str , name : str , namespace : str ):
        try:
            cmd = f"kubectl get {resource} {name} -n {namespace} -o json"
            result = subprocess.run(cmd , text=True, capture_output=True , shell=True) 
            return json.loads(result.stdout) 
        except Exception as e:
            print("Couldn't get POD in JSON format")

def waiting_check_error(error , resource  , name , namespace):
    result = get_pod_json(resource , name , namespace) 
    # print("Printing Result" , result)
    containers = result['status']['containerStatuses'] 
    for c in containers:
        if 'waiting' in c['state'] and c['state']['waiting']['reason'] == error:
            return True 
    
    return False 


def get_exitcode(data):
     containers = data['status']['containerStatuses'] 
     for c in containers:
          if 'lastState' in c and 'terminated' in c['lastState'] and 'exitCode' in c['lastState']['terminated']:
               return c['lastState']['terminated']['exitCode']
          
     return None