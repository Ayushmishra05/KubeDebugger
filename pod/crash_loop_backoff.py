import yaml 
import subprocess


class DetectCrashLoopBackOff:
    def __init__(self, pod : str , namespace: str, data : str):
        self.pod = pod 
        self.namespace = namespace
        self.data = data 
        
    def detect_crash_loop_backoff(self):
        cmd = f"kubectl describe pod {self.pod} -n {self.namespace} | grep -i crashloopbackoff" 
        result = subprocess.run(cmd, capture_output=True, text=True, shell = True) 
        if result.returncode == 0:
            print("1. The Issue is related to CrashLoopBackOff (A very common issue in K8S)") 
            print("2. Let's Diagnose")
            isCmdIssue : bool = self.detect_command_issue()
            if isCmdIssue:
                return True 
            isCmdExecIssue : bool = self.detect_command_executable_issue()
            if isCmdExecIssue:
                return True
            isError1 : bool = self.detect_exit_code_1()
            if isError1:
                return True 
            isError2 : bool = self.detect_exit_code_2()
            if isError2:
                return True
        else:
            return False


    def detect_command_issue(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)
        if int(result.stdout) == 127:
            print("***Got it, This is something related to the command which you have used ***\n")
            print("📌 Suggestion")
            print("1. Check with your Command inside the Pod Definition file") 
            print("2. If your command is correct then this might be related to application level command failure")
            print("3. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
        
    def detect_command_executable_issue(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)
        if int(result.stdout) == 126:
            print("***Got it, This is something related to the command which you have used ***\n")
            print("📌 Suggestion")
            print("1. If you have used command inside your pod Definition file, is is the possibility that your command doesn't have executable bit")
            print("2. Check with your Command inside the Pod Definition file") 
            print("3. If your command is executable then this might be related to application level command failure")
            print("4. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 

    def detect_exit_code_1(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)
        if int(result.stdout) == 1:
            print("***Got it, This is something related to your application***")
            print("***Seems like your application has crashed due to some mismatch in logic or syntactical error, check with your application code***\n")
            print("📌 Suggestion")
            print("1. Check Exceptions, logical Errors or any Syntactical Errors inside your application")
            print("2. Check Scripts Inside your Application") 
            print("3. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
        
    def detect_exit_code_2(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)
        if int(result.stdout) == 2:
            print("***Got it, Some Shell script inside your application might have failed to execute***\n")
            print("📌 Suggestion")
            print("1. Check Exceptions, logical Errors or any Syntactical Errors inside your Application shell Scripts")
            print("2. Use --explain with your command to get the exact answer about your error")
            return True 
        else:
            return False 
    


    """Exit code 139 corresponds to the OOM Killed Error, When the Memory is over utilized by a resource Linux kills the process, and returns 139"""
    def detect_exit_code_139(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True) 
        if int(result.stdout) == 137:
            print("***This Error occured, because your pod didn't have sufficient memory to execute ***") 
            print("📌 Suggestion")
            print("1. Check with the Limits and Requests in the Pod")
            print("2. Check Whether your node has sufficient memory ") 
            print("3. Try to increase the memory for the pod for it to run seamlessly") 
            print("4. Use --explain for deeper analysis")
            return True
        else:
            return False 
    

    def detect_probe_failed(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "probe failed" """ 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True)  
        if result.returncode == 0:
            print("The issue caused because the probe failed, in your pod") 
            return True 
        else:
            return False 
    
    def detect_instant_crash(self):
        cmd = f"""kubectl describe pod {self.pod} -n {self.namespace} | grep -i "Last State" -A 10 | grep -i "Exit Code" | awk '{{print $3}}'""" 
        result = subprocess.run(cmd, text=True, capture_output= True, shell= True) 
        isProbeFailed = self.detect_probe_failed()
        if int(result.stdout) == 0 and not isProbeFailed:  
            print("***Your pod got executed Successfully, but crashed immediately***") 
            print("Kubernetes Expects Long Running pods, short Running Pods Causes CrashLoopBackOff")       
            print("📌 Suggestion")
            print("1. Check the Pod Logic, and run the pod again") 
            print("2. Use --explain for granular insights") 
            return True
        else:
            return False
        
    








