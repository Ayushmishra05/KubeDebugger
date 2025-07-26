from kube_debugger.utils.config import GREEN , YELLOW , BOLD , RESET , RED
from kube_debugger.pod.detect_exit_code import DetectExitCode
from kube_debugger.pod.pod_utils import waiting_check_error
import subprocess
import yaml 

class DetectCrashLoopBackOff:
    def __init__(self, pod : str , namespace: str, data : str, kind : str):
        self.pod = pod 
        self.namespace = namespace
        self.data = data 
        self.kind = kind
        self.error = "CrashLoopBackOff"
        
    def detect_crash_loop_backoff(self):
        error = waiting_check_error(self.error , self.kind , self.pod , self.namespace) 
        if error:
            print(f"{RED}1. The Issue is related to CrashLoopBackOff (A very common issue in K8S){RESET}") 
            print(f"{GREEN}2. Let's Diagnose{RESET}")
            exit_code_detector = DetectExitCode(self.data , self.pod , self.namespace , self.kind) 
            isExitCodeIssue = exit_code_detector.detect_exit_code() 
            if isExitCodeIssue:
                return True
        else:
            return False








