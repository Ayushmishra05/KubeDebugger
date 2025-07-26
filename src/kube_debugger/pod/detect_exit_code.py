from kube_debugger.pod.pod_utils import waiting_check_error, get_pod_json, get_exitcode
from kube_debugger.utils.config import BOLD, RESET
import subprocess 


class DetectExitCode:
    def __init__(self , data: str , pod: str , namespace: str , kind ):
        self.data = data 
        self.pod = pod 
        self.namespace = namespace
        self.kind = kind
        self.error = "CrashLoopBackOff" 
    
    def detect_codes(self , containers : dict):
        for container in containers:
            if 'lastState' in container and 'terminated' in container['lastState']: 
                return container['lastState']['terminated']['exitCode'] 
        return None 
                
    
    def detect_exit_code(self):
        try:
            checks = [
                self.detect_command_issue,
                self.detect_command_executable_issue,
                self.detect_exit_code_1,
                self.detect_exit_code_2,
                self.detect_exit_code_139,
                self.detect_probe_failed,
                self.detect_instant_crash,
            ]

            for check in checks:
                result = check()
                if result:
                    return True

            return False

        except AttributeError as e:
            print(f"❌ Method missing in DetectExitCode class: {e}")
            raise

        except Exception as e:
            print(f"❌ Unexpected error during exit code detection: {e}")
            raise
    
    def detect_command_issue(self):
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        if exitcode is not None and exitcode == 127:
            print(f"{BOLD}Got it, This is something related to the command which you have used {RESET}\n")
            print("📌 Suggestion")
            print("1. Check with your Command inside the Pod Definition file") 
            print("2. If your command is correct then this might be related to application level command failure")
            print("3. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
        
    def detect_command_executable_issue(self):
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        if exitcode is not None and exitcode == 126:
            print(f"{BOLD}Got it, This is something related to the command which you have used {RESET}\n")
            print("📌 Suggestion")
            print("1. If you have used command inside your pod Definition file, is is the possibility that your command doesn't have executable bit")
            print("2. Check with your Command inside the Pod Definition file") 
            print("3. If your command is executable then this might be related to application level command failure")
            print("4. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 

    def detect_exit_code_1(self):
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        # print("Printing Exit Code " , exitcode)
        if exitcode is not None and exitcode == 1:
            print(f"{BOLD}Got it, This is something related to your application")
            print(f"Seems like your application has crashed due to some mismatch in logic or syntactical error, check with your application code{RESET}\n")
            print("📌 Suggestion")
            print("1. Check Exceptions, logical Errors or any Syntactical Errors inside your application")
            print("2. Check Scripts Inside your Application") 
            print("3. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
        
    def detect_exit_code_2(self):
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        if exitcode is not None and exitcode == 2:
            print(f"{BOLD}Got it, Some Shell script inside your application might have failed to execute {RESET}\n")
            print("📌 Suggestion")
            print("1. Check Exceptions, logical Errors or any Syntactical Errors inside your Application shell Scripts")
            print("2. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
    


    """Exit code 139 corresponds to the OOM Killed Error, When the Memory is over utilized by a resource Linux kills the process, and returns 139"""
    def detect_exit_code_139(self):
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        if exitcode is not None and exitcode == 137:
            print(f"{BOLD}This Error occured, because your pod didn't have sufficient memory to execute {RESET}") 
            print("📌 Suggestion")
            print("1. Check with the Limits and Requests in the Pod")
            print("2. Check Whether your node has sufficient memory ") 
            print("3. Try to increase the memory for the pod for it to run seamlessly") 
            print("4. Use --explain for deeper analysis")
            return True
        else:
            return False 
    

    def detect_probe_failed(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace}""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)  
        if result.returncode == 0 and result.stdout == "probe failed":
            print("The issue caused because the probe failed, in your pod") 
            return True 
        else:
            return False 
    
    def detect_instant_crash(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace}""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True) 
        isProbeFailed = self.detect_probe_failed()
        data = get_pod_json(self.kind , self.pod  , self.namespace)
        exitcode = get_exitcode(data)
        if exitcode is not None and exitcode == 137 and  isProbeFailed: 
            print(f"{BOLD}Your pod got executed Successfully, but crashed immediately{RESET}") 
            print("Kubernetes Expects Long Running pods, short Running Pods Causes CrashLoopBackOff")       
            print("📌 Suggestion")
            print("1. Check the Pod Logic, and run the pod again") 
            print("2. Use --explain for granular insights") 
            return True
        else:
            return False