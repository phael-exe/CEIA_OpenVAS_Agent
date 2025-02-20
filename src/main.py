from api import LLM
from tools import ResultManager, GVMWorkflow


query = input("User: ")

def get_response_from_openai(message):

    llm = LLM().connect_openai()
    
    response = llm.invoke(message)
    
    return response

#TESTE
"""response = get_response_from_openai(query)
print("Assistant:", response.content)"""
