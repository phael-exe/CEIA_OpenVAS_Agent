import os
import webbrowser

from dotenv import load_dotenv
from src.tools.gvm_workflow import GVMWorkflow
from src.tools.gvm_results import ResultManager
from src.tools.art import art_main

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def get_response_from_openai(message):

    llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature=0.1,
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
    result_manager = ResultManager()
    context = result_manager.result()
    
    messages = [
        SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning 
                      and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability 
                      scanning tool, your role is to interpret everything that comes within context """),
        HumanMessage(content=f"Please analyze the following OpenVAS scan result: {context}, using {question}")
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
    
    return workflow.run()
   
toolkit = [create_OpenVAS_tasks, get_OpenVAS_results]

llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature=0.1,
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

agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=False)

art_main()

while True:
    query = input("\nUser: ")

    if query.lower() in ["q", "exit"]:
        print("\nExiting chat...\n")
        break

    result = agent_executor.invoke({"input": query})
    print(f"\n{result["output"]}\n")