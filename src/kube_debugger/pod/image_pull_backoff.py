from kube_debugger.utils.config import GREEN, RED, RESET, BOLD, YELLOW
from kube_debugger.pod.pod_utils import waiting_check_error, get_pod_json
from kube_debugger.utils.ai_init import ai_module
from typing import List 
import subprocess 
import requests
import yaml 

class ImagePullBackOffError:
    def __init__(self, pod_name : str , namespace : str , data : str , explain : str, kind : str):
        self.pod_name = pod_name 
        self.namespace = namespace 
        self.data = data 
        self.explain = explain
        self.kind = kind 
        self.error_type = "ImagePullBackOff" 
        self.error_type2 = "ErrImagePull"
    
    def list_all_images_in_pod(self) -> List:
        pod_data = yaml.safe_load(self.data) 
        containers = pod_data.get('spec' , {}).get('containers' , []) 
        init_containers = pod_data.get('spec' , {}).get('initContainers' , []) 
        images = []
        for ele in containers:
            if 'image' in ele:
                images.append(ele['image']) 
        if len(init_containers) != 0:
            for ele in init_containers:
                if 'image' in ele:
                    images.append(ele['image']) 
        return images 
    
    def check_basic_ip(self):
        cmd = ["ping" , "8.8.8.8"]
        result = subprocess.run(cmd , capture_output=True , text=True) 
        # print("Ping result" , result)
        if result.returncode != 0 or "Destination host unreachable" in result.stdout:
            print(f"{YELLOW}{BOLD}⚠️  There Seems to be a Network Issue While pulling the Image  {RESET}") 
            return True 
        else:
            return False
    

    def check_network_connectivity(self):
        cmd = ["nslookup" , "google.com"]
        result = subprocess.run(cmd , capture_output=True , text=True) 
        # print("NS lookup output " , result)
        if result.returncode != 0 or "No response from server" in result.stdout :
            print(f"{YELLOW}{BOLD}⚠️  It looks Like your DNS is broken, check your firewall and DNS Seetings {RESET}") 
            return True 
        else:
            return False 

        
    def check_https_connectivity(self):
        cmd = ["curl" , "https://www.google.com"]
        result = subprocess.run(cmd , capture_output=True , text=True) 
        
        if  result.returncode != 0 or "Could not resolve host" in result.stdout:
            print(f"{YELLOW}{BOLD}⚠️  Their Seems to be a Firewall or DNS Config Issue {RESET}") 
            return True 
        else:
            return False 
        
    

    def check_image_pull_backoff(self) -> bool:
        error1 = waiting_check_error(self.error_type, self.kind , self.pod_name , self.namespace) 
        error2 = waiting_check_error(self.error_type2 , self.kind , self.pod_name , self.namespace)
        if  error1 or error2:
            if self.explain:
                self.explain_feature()
                return True 
            images = self.list_all_images_in_pod() 
            isIP = self.check_basic_ip() 
            if isIP == True:
                return True 
            isDNS = self.check_network_connectivity() 
            if isDNS == True:
                return True 
            isHTTPS = self.check_https_connectivity() 
            if isHTTPS == True:
                return True 
            isValidImage = self.check_image_authenticity(images) 
            if isValidImage == False:
                return True
            print(isDNS , isHTTPS  , isIP , isValidImage) 
        else:
            # print("Error " , result.stderr)
            return False

    def parse_image_name(self, image: str):
        namespace = "library"
        tag = "latest"
        if ":" in image:
            image, tag = image.rsplit(":", 1)
        if "/" in image:
            namespace, repo = image.split("/", 1)
        else:
            repo = image
        return namespace, repo, tag


    def check_image_authenticity(self , images : str):

        total_check = False
        inner_check = False

        for image in images:
            namespace, repo, tag = self.parse_image_name(image)
            url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/tags/{tag}"

            result = requests.get(url=url) 
            if result.status_code == 200:
                inner_check = True 
            elif result.status_code == 404:
                print(f"{YELLOW}{BOLD}⚠️  Seems like You have used Wrong Image {image}, Check the Image name and tag details properly{RESET}")
                total_check = False
            else:
                print(f"Your Image {image} couldn't be verified try Again, this could be due to internal network issues")
                total_check = False 
        if total_check == False:
            return False 
        elif inner_check:
            return True
    
    def explain_feature(self):
        output = get_pod_json("pod" , self.pod_name , self.namespace)
        ai_module(description="NA" , logs="NA" , yaml_file=str(output)) 
