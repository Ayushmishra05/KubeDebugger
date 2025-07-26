# K8S-Debugger: Diagnose-Your-K8S-Environment
K8S-Debugger is a Kubernetes Diagnosing tool, which helps developers debug what's wrong with their cluster, This will save developers time, as they don't have to deep dive into Logs and try to understand as K8S-Debugger does it for you 

## Version 0.0.1 Features 

1) **Pod Debugging** : The V1 is a start of the project, and this is only going to debug the pod based issues, although there are multiple pod based issues that can occur in a kubernetes cluster, but Apparently most frequent and most occuring errors have been included in this iteration 

2) **AI Feature** : Some Pod based errors in K8S cluster might not be detected by the tool. In that case i would highly encourage you to use --explain feature, ensure to setup GROQ_API_KEY before using the --explain feature 


## Installation 
### PIP Installation
```python
pip install kube-debugger
```
### Git Setup 
**Create venv** 

On Windows 
```bash 
python -m venv venv
venv/Scripts/activate
```

On Linux/MacOs
```bash
python3 -m venv venv
source venv/bin/activate
```

**Clone Repo** 

```bash
git clone https://github.com/Ayushmishra05/KubeDebugger.git 
```


## GROQ API KEY SETUP 

- **Step 1:** Head over to [groq.com](https://groq.com) and get your free API KEY

- **Step 2:** Setup GROQ_API_KEY in your system environment variables 

``` bash
export GROQ_API_KEY=<api_key> 
```
`
⚠️ Remember:  AI is an Experimental feature, and we will soon rollout the working Version 
`

## Contributions are Encouraged 

- I would love to know your perspective 
- Create a Pull Request or reach out to me at ayush89718@gmail.com 
- Star the Repository for future references



#### Made with ❤️ for K8S Community by Ayush Mishra
