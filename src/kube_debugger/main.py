from kube_debugger.pod.crash_loop_backoff import DetectCrashLoopBackOff
from kube_debugger.pod.image_pull_backoff import ImagePullBackOffError 
from kube_debugger.pod.detect_exit_code import DetectExitCode
from kube_debugger.pod.config_error import ConfigError
from dotenv import load_dotenv
from typing import Optional
import subprocess
import typer 
import yaml 
import sys
import os
import re

load_dotenv() 

api_key = os.environ.get('GROQ_API_KEY')

app = typer.Typer() 

@app.command(help="Pod Utility helps you debug pod objects in K8S") 
def pod(name : str , namespace : str = typer.Option("default" , "--namespace" , "-n" , help="Namespace where the current resource is present, checks in the DEFAULT namespace, by default") , explain : bool = typer.Option(False , "--explain" , help="Enable this option to get the deeper analysis")):
    command = ["kubectl" , "get" , "pod" , name , "-n" , namespace , "-o"  , "yaml"] 
    result = subprocess.run(command , capture_output=True, text=True)
    kind = "pod"
    if result.returncode == 0:
        if ImagePullBackOffError(name , namespace , result.stdout, explain , kind).check_image_pull_backoff():
            return

        elif DetectCrashLoopBackOff(name , namespace , result.stdout , kind).detect_crash_loop_backoff():
            return

        elif ConfigError(name , namespace , result.stdout, kind).detect_config_error():
            return

        elif DetectExitCode(result.stdout , name , namespace, kind).detect_exit_code():
            return

    else:
        print("*** ❌ K8S-Debugger couldn't process your K8S Cluster ***")
        return result.stderr 


    



    



@app.command(help="Deployments utility helps you debug the deployment related objects")
def deployment(name: str):

    print(f"deployment name {name}")

if __name__ == "__main__":
    app()