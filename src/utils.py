import typer 
from typing import Optional
import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pod.image_pull_backoff import ImagePullBackOffError
import yaml 
app = typer.Typer() 



@app.command(help="Pod Utility helps you debug pod objects in K8S") 
def pod(name : str , namespace : str = typer.Option("default" , "--namespace" , "-n" , help="Namespace where the current resource is present, checks in the DEFAULT namespace, by default")):
    # print("Inside Func")
    command = ["kubectl" , "get" , "pod" , name , "-n" , namespace , "-o"  , "yaml"] 
    try:
        result = subprocess.run(command , capture_output=True, text=True)
    except Exception as e:
        raise e 
    # print(result.stdout)
    if result.returncode == 0:
        image_pull_error_checker = ImagePullBackOffError(name , namespace , result.stdout) 

        isImagePullBackOff = image_pull_error_checker.check_image_pull_backoff() 
        if isImagePullBackOff:
            print("***⚠️ The issue was related to Image Pull By docker ***")
    else:
        print("*** ❌ K8S-Debugger couldn't process your K8S Cluster ***")
        return result.stderr 


    


@app.command(help="Deployments utility helps you debug the deployment related objects")
def deployment(name: str):
    print(f"deployment name {name}")

if __name__ == "__main__":
    app()