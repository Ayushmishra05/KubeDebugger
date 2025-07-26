from setuptools import setup, find_packages
import os 
from pathlib import Path


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name='kube-debugger',
    version='0.0.5',  
    author='Ayush Mishra A',
    author_email='ayush89718@gmail.com',
    description='Kube-Debugger is a Kubernetes CLI Tool which will help you debug your cluster',
    long_description=long_description,  
    long_description_content_type='text/markdown',
    url='https://github.com/Ayushmishra05/KubeDebugger', 
    packages=find_packages(exclude=['tests*'] , where="src"), 
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'debug = kube_debugger.main:app',
        ],
    },
    install_requires= [
        'langchain_core==0.3.72',
        'langchain_groq==0.3.6',
        'python-dotenv==1.1.1',
        'PyYAML==6.0.1',
        'Requests==2.32.4',
        'setuptools==69.5.1',
        'typer==0.16.0'
    ], 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    license='MIT', 
)
