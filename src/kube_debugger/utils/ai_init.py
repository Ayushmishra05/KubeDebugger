from langchain_core.output_parsers import JsonOutputParser, StrOutputParser 
from kube_debugger.utils.config import RED, BOLD, GREEN, RESET
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq.chat_models import ChatGroq
import re


def ai_module(description : str , logs : str , yaml_file : str):
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
        ("user", "I have been facing this issue {describe} , logs --> {logs} , file --> {yaml_file}")
    ])
    model = ChatGroq(model="qwen/qwen3-32b") 
    parser = JsonOutputParser() 
    str_parser = StrOutputParser()

    chain = prompt_template | model | str_parser 

    result = chain.invoke({'describe' : description , 'logs' : logs , 'yaml_file' : yaml_file}) 
    result = re.sub(r'<think>.*?</think>' , '' , result , flags=re.DOTALL) 
    result = parser.parse(result) 
    print(f"\n{RED}{BOLD}❌ Issue Found{RESET}")
    for ele in result['issue']:
        print(f"- {ele}{RESET}")

    print(f"\n{GREEN}{BOLD}📌 Suggestions{RESET}")
    for ele in result['answer']:
        print(f"- {ele}{RESET}")




