import requests
import re

def parse_image_name(image: str):
    # Default values
    namespace = "library"
    tag = "latest"

    # If tag is present
    if ":" in image:
        image, tag = image.rsplit(":", 1)

    # If user provides namespace (like ayush/nginx)
    if "/" in image:
        namespace, repo = image.split("/", 1)
    else:
        repo = image

    return namespace, repo, tag


def check_uri(image : str):
    namespace, repo, tag = parse_image_name(image)
    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/tags/{tag}"

    result = requests.get(url=url) 
    if result.status_code == 200:
        print("Image Exists and Verified") 
    elif result.status_code == 404:
        print("Image doesn't exist") 
    else:
        print("Couldn't Verify the Image")


check_uri("mishrrayush/learning-repo:static")