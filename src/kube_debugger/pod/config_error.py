from kube_debugger.pod.pod_utils import get_pod_json , get_exitcode
from kube_debugger.utils.config import RESET , RED
import subprocess 
import json 
import re


YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"


"""Run Container Error Detection : One of the Common Errors in Kubernetes, can happen because of multiple reasons 
   Invalid Config File, Config File Doesn't exist, Secret Key Doesn't Exist
"""

class ConfigError:
    def __init__(self , pod : str, namespace : str, data : str, kind : str):
        self.pod = pod 
        self.namespace = namespace 
        self.data = data 
        self.kind = kind
    

    def get_pod_json(self , resource : str , name : str , namespace : str ):
        try:
            cmd = f"kubectl get {resource} {name} -n {namespace} -o json"
            result = subprocess.run(cmd , text=True, capture_output=True , shell=True) 
            return json.loads(result.stdout) 
        except Exception as e:
            print(f"{RED}Couldn't get POD in JSON format{RESET}")
    

    def has_create_container_error(self, json_data):
        containers = json_data.get("status", {}).get("containerStatuses", [])
        for c in containers:
            waiting = c.get("state", {}).get("waiting")
            if waiting and waiting.get("reason") == "CreateContainerConfigError":
                return True
        return False

    def detect_config_error(self):
        result = self.get_pod_json(self.kind , self.pod, self.namespace) 
        # print(result)
        # print(self.has_create_container_error(result))
        if self.has_create_container_error(result):
            print(f"{YELLOW}{BOLD}This is Something Related to CONFIGURATION based issues{RESET}") 
            isConfigMap = self.detect_configmap_not_found() 
            isConfigMapKey = self.detect_config_key_error() 
            isSecret = self.detect_secret_error() 
            isSecretKey = self.detect_secret_key_error()
            if isConfigMap or isConfigMapKey or isSecret or isSecretKey:
                return True 
            else:
                return False
        
    
    def detect_configmap_not_found(self):
        data = get_pod_json(self.kind , self.pod , self.namespace) 
        containers = data['status']['containerStatuses'] 
        message = None
        for c in containers:
            if 'waiting' in c['state'] and 'message' in c['state']['waiting']:
                message =  c['state']['waiting']['message']
                break 
        pattern = r'^configmap "([^"]+)" not found$'
        match = re.match(pattern , message)
        if message is not None and match:
            print(f"⚠️  Apparently Configmap \"{match.group(1)}\" doesn't exist in the \"{self.namespace}\" namespace") 
            print(f"{BOLD}🤔  Let me Check in Other Namespaces{RESET}")  

            cmd = f"kubectl get configmap -A -o json" 
            result = subprocess.run(cmd , text=True, capture_output=True, shell=True)
            if result.returncode == 0: 
                data = json.loads(result.stdout) 
                found = False 
                for item in data['items']:
                    if item['metadata']['name'] == match.group(1):
                        print(f"✅  Apparently The Configmap exist in \"{item['metadata']['name']}\" namespace , and your pod is in \"{self.namespace}\" namespace") 
                        found = True 
                        break 
                
                if not found:
                    print(f"🤔 Seems Like You haven't Created the Configmap \"{match.group(1)}\"")  
                print(f"\n📌 {GREEN}{BOLD}Suggestions {RESET}") 
                print(f"{BOLD}1. Create the Configmap name in the right Namespace")
                print(f"2. Create the ConfigMap if you haven't created{RESET}") 

            return True 
        
        else:
            return False
    
    def detect_config_key_error(self):
        data = get_pod_json(self.kind , self.pod , self.namespace) 
        containers = data['status']['containerStatuses'] 
        message = None
        for c in containers:
            if 'waiting' in c['state'] and 'message' in c['state']['waiting']:
                message =  c['state']['waiting']['message']
                break 
        pattern = r"couldn't find key (\S+) in ConfigMap (\S+)/(\S+)"
        match = re.match(pattern, message)

        if message is not None and match:
            print(f" Seems Like You Inserted Wrong key named \"{match.group(1)}\" in your ConfigMap \"{match.group(2)}\"") 
            configmap_key = match.group(1)
            configmap_namespace = match.group(2)
            configmap_name = match.group(3)  
            
            get_keys = f"kubectl get configmap {configmap_name} -n {configmap_namespace} -o json" 
            get_keys_run  = subprocess.run(get_keys, shell = True, capture_output=True, text=True) 
            if get_keys_run.returncode == 0:
                data = json.loads(get_keys_run.stdout)['data']
                data_keys = data.keys() 
                print(f"📌 These are the List of Keys present in your ConfigMap \"{", ".join(list(data_keys))}\"") 
            else:
                print(f"Couldn't get configmap \"{configmap_name}\"") 
            
            print(f"\n📌 {GREEN}{BOLD}Suggestions {RESET}") 
            print(f"{BOLD}1. Check Your ConfigMap and Check with the Keys")
            print(f"2. Check The Key name which you have used in your ConfigMaps{RESET}")
            return True
        else:
            return False

                

    def detect_secret_error(self):
        data = get_pod_json(self.kind , self.pod , self.namespace) 
        containers = data['status']['containerStatuses'] 
        message = None
        for c in containers:
            if 'waiting' in c['state'] and 'message' in c['state']['waiting']:
                message =  c['state']['waiting']['message']
                break 
        pattern = r'^secret "([^"]+)" not found$'
        match = re.match(pattern , message)
        if message is not None and match:
            print(f"⚠️ Apparently Secret \"{match.group(1)}\" doesn't exist in the \"{self.namespace}\" namespace") 
            print("🤔  Let me Check in Other Namespaces")  

            cmd = f"kubectl get secret -A -o json" 
            result = subprocess.run(cmd , text=True, capture_output=True, shell=True)
            if result.returncode == 0: 
                data = json.loads(result.stdout) 
                found = False 
                for item in data['items']:
                    if item['metadata']['name'] == match.group(1):
                        print(f"✅ Apparently The Secret exist in \"{item['metadata']['name']}\" namespace , and your pod is in \"{self.namespace}\" namespace") 
                        found = True 
                        break 
                
                if not found:
                    print(f"🤔 Seems Like You haven't Created the Secret \"{match.group(1)}\"")  
                print(f"\n📌 {GREEN}{BOLD}Suggestions {RESET}") 
                print(f"{BOLD}1. Create the Secret in the right Namespace")
                print(f"2. Create the Secret if you haven't created{RESET}") 

            return True 
        
        else:
            return False
        


    
    def detect_secret_key_error(self):
        data = get_pod_json(self.kind , self.pod , self.namespace) 
        containers = data['status']['containerStatuses'] 
        message = None
        for c in containers:
            if 'waiting' in c['state'] and 'message' in c['state']['waiting']:
                message =  c['state']['waiting']['message']
                break 
        pattern = r"couldn't find key (\S+) in Secret (\S+)/(\S+)"
        match = re.match(pattern, message)

        if message is not None and match:
            print(f" Seems Like You Inserted Wrong key named \"{match.group(1)}\" in your Secret \"{match.group(2)}\"") 
            secret_key = match.group(1)
            secret_namespace = match.group(2)
            secret_name = match.group(3)  
            
            get_keys = f"kubectl get secret {secret_name} -n {secret_namespace} -o json" 
            get_keys_run  = subprocess.run(get_keys, shell = True, capture_output=True, text=True) 
            if get_keys_run.returncode == 0:
                data = json.loads(get_keys_run.stdout)['data']
                data_keys = data.keys() 
                print(f"📌 These are the List of Keys present in your Secret \"{", ".join(list(data_keys))}\"") 
            else:
                print(f"Couldn't get configmap \"{secret_name}\"") 
            
            print(f"\n📌 {GREEN}{BOLD}Suggestions {RESET}") 
            print(f"{BOLD}1. Check Your Secret and Check with the Keys")
            print(f"2. Check The Key name which you have used in your Secret{RESET}")
            return True
        else:
            return False
