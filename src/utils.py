import typer 
from typing import Optional
import subprocess
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pod.image_pull_backoff import ImagePullBackOffError 
from pod.crash_loop_backoff import DetectCrashLoopBackOff
import yaml 
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser 
import re
from dotenv import load_dotenv
import os 
load_dotenv() 

api_key = os.environ['GROQ_API_KEY']

app = typer.Typer() 

@app.command(help="Pod Utility helps you debug pod objects in K8S") 
def pod(name : str , namespace : str = typer.Option("default" , "--namespace" , "-n" , help="Namespace where the current resource is present, checks in the DEFAULT namespace, by default") , explain : bool = typer.Option(False , "--explain" , help="Enable this option to get the deeper analysis")):
    command = ["kubectl" , "get" , "pod" , name , "-n" , namespace , "-o"  , "yaml"] 
    result = subprocess.run(command , capture_output=True, text=True)
    if explain:
        describe = subprocess.run(f"kubectl describe pod {name} -n {namespace}" , capture_output=True, shell=True, text=True)
        yaml_file = subprocess.run(f"kubectl logs {name} -n {namespace} --previous", capture_output=True, shell=True, text=True)
        if describe.returncode == 0 and result.returncode == 0 and yaml_file.returncode == 0:
            explain_feature(describe=describe.stdout , logs = result.stdout , yaml_file = yaml_file.stdout)
    elif result.returncode == 0:
        image_pull_error_checker = ImagePullBackOffError(name , namespace , result.stdout) 
        crash_loop_error_checker = DetectCrashLoopBackOff(name , namespace , result.stdout)
        isImagePullBackOff = image_pull_error_checker.check_image_pull_backoff() 
        isCrashLoopBackOff = crash_loop_error_checker.detect_crash_loop_backoff()
        if isImagePullBackOff:
            print("***⚠️ The issue was related to Image Pull By docker ***")
        elif isCrashLoopBackOff:
            print("***⚠️ Issue was related to Crash Loop Back Off")
    else:
        print("*** ❌ K8S-Debugger couldn't process your K8S Cluster ***")
        return result.stderr 


    
def explain_feature(describe : str, logs : str , yaml_file : str):
    prompt_template = ChatPromptTemplate([
    ("system", "You are an Expert Kubernetes Debugger, you have been awarded with the top kubernetes engineer awards, you can understand any problem by looking at the yaml file + logs + description, "
    "you know how to deal with clusters, you know the answers for kind of every kubernetes related problem, "
    "because you have been through it, now a user comes with a error to you, and looking at some of the data, "
    "that he will provide, you have to answer his question"
    "you need to return the output in json format, no extras, no starting nothing, only json output, the json should contain only two keys one is the key named issue, where you are telling what are the issue, and why is that caused and second is the key named "
    "answer"
    "where you are giving them suggestions, and helping them debug it, "
    "and the value as your answer, you are not allowed to elaborate on any point, just provide the answer with 5 - 6 bullet points and that's it, ans the issue with also some bullet points"
    "make it crisp, concise and straight to the point, you have to tell user, what he should do to debug it "
    "Point the Exact location, from where the issue is being caused"),
    ("user", "I have been facing this issue {describe} , logs --> {logs} , yaml_file --> {yaml_file}")
])
    model = ChatGroq(model="qwen/qwen3-32b") 
    parser = JsonOutputParser() 
    str_parser = StrOutputParser()

    chain = prompt_template | model | str_parser 
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    BLUE = "\033[94m"

    data = {
        "describe" : describe, 
        "logs" : logs, 
        "yaml_file" : yaml_file
    }

    result = chain.invoke(data) 
    result = re.sub(r'<think>.*?</think>' , '' , result , flags=re.DOTALL) 
    result = parser.parse(result) 
    print(f"\n{RED}{BOLD}❌ Issue Found{RESET}")
    for ele in result['issue']:
        print(f"- {ele}{RESET}")

    print(f"\n{GREEN}{BOLD}📌 Suggestions{RESET}")
    for ele in result['answer']:
        print(f"- {ele}{RESET}")

    



@app.command(help="Deployments utility helps you debug the deployment related objects")
def deployment(name: str):

    print(f"deployment name {name}")

if __name__ == "__main__":
    app()