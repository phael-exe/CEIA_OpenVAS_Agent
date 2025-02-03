import os
from dotenv import load_dotenv
from gvm_workflow import GVMWorkflow
from gvm_results import ResultManager


from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

query = input("User: ")

def get_response_from_openai(message):

    llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature=0.2,
        max_completion_tokens=None,
        timeout=None,
        api_key=api_key,
        )
    
    response = llm.invoke(message)
    
    return response

@tool
def get_OpenVAS_results(question: str):
    """
    This tool assists in interpreting an OpenVAS scan result. It helps automate the analysis and understanding 
    of the vulnerability data extracted from the OpenVAS scan results in the string
    """
   
    context =  ResultManager.result()
   
    messages = [
        SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning 
                      and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability 
                      scanning tool, your role is to interpret everything that comes within the string of 
                      an XML result converted from an OpenVAS scan. Do not skip any detail—automatically 
                      analyze and extract all relevant vulnerability data from the string, ensuring nothing 
                      is overlooked. Your task is to ensure that every piece of information within the OpenVAS 
                      scan result is processed thoroughly and accurately, providing users with complete insights into the scans
                      findings. Be emphatic in your approach, making sure no important data is missed, and offering precise 
                      analysis for effective vulnerability assessment. You have to hide the response of result_str"""),
        HumanMessage(content=f"Please analyze the following OpenVAS scan result: {context}, using{question}")
    ]
    
    response = get_response_from_openai(messages)
    
    return response

@tool
def create_OpenVAS_tasks(question: str):
    """
    This tool helps create tasks in OpenVAS, a vulnerability scanning tool.
    It will assist in automating task creation for network scans and pentesting tasks within OpenVAS.
    """
    workflow = GVMWorkflow()
    
    context =  workflow.run()
   
    messages = [
        SystemMessage(content="""You are a cybersecurity assistant specialized in network scanning and penetration testing. 
                                  You are an expert in using OpenVAS, a powerful vulnerability scanning tool, and have in-depth knowledge 
                                  of its functionalities, including task automation and management. Your role is to assist with automating 
                                  the creation of tasks in OpenVAS, guiding the user through setting up scans, configuring targets, 
                                  and scheduling tasks to ensure optimal vulnerability assessments. You should provide clear, concise instructions 
                                  and troubleshooting tips for configuring OpenVAS tasks, helping users streamline their security operations effectively. 
                                  Additionally, you should offer suggestions on best practices for network scanning and pentesting using OpenVAS, 
                                  based on the user's specific needs."""),
        HumanMessage(content=f"Execute the following task: {context}, using{question}")
    ]
    
    response = get_response_from_openai(messages)
    
    return response

toolkit = [create_OpenVAS_tasks, get_OpenVAS_results]

llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature=0.2,
        max_completion_tokens=None,
        timeout=None,
        api_key=api_key,
        )


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
                        You are a cybersecurity assistant specialized in network scanning and penetration testing. 
                        You are an expert in using OpenVAS. Use your tools to answer questions.
                        Please generate a response organized in bullet points, with headings and lists to make it easier to read.
                        
                        Return only a message with the task created.
         """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
        
    ]
)

agent = create_openai_tools_agent(llm, toolkit, prompt)

agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=True)

result = agent_executor.invoke({"input":f"{query}"})

print(result["output"])