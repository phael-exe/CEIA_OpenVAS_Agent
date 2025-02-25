import os
import webbrowser

from dotenv import load_dotenv
from src.tools.gvm_workflow import GVMWorkflow
from src.tools.gvm_results import ResultManager

from langchain.memory import ConversationBufferMemory
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
   
    context =  result_manager.result()
   
    messages = [
        SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning 
                      and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability 
                      scanning tool, your role is to interpret everything that comes within the string of 
                      an XML result converted from an OpenVAS scan. Do not skip any detail—automatically 
                      analyze and extract all relevant vulnerability data from the string, ensuring nothing 
                      is overlooked. Your task is to ensure that every piece of information within the OpenVAS 
                      scan result is processed thoroughly and accurately, providing users with complete insights into the scans
                      findings. Be emphatic in your approach, making sure no important data is missed, and offering precise 
                      analysis for effective vulnerability assessment. You have to hide the response of result_str
                      
                      You are a cybersecurity assistant specializing in vulnerability analysis and reporting. 
                      Your task is to provide detailed information about detected vulnerabilities in a structured format.

                      When responding, follow this template and replace the placeholders with the appropriate values:

                        Vulnerability: [Name of the vulnerability, typically from databases like CVE, descriptive and concise]

                        ID: [Unique identifier for the vulnerability within the reporting system]
                        Host: _[IP address of the affected host, optionally including an identifier such as "_gateway" or "webserver"]
                        Port: [Affected port number and protocol (e.g., 443/tcp)]
                        CVSS Base Score: [Severity score based on the CVSS scale, indicating if it is low, medium, high, or critical]
                        Description: [Brief technical explanation of the vulnerability, including its cause and potential impacts, such as remote code execution, XSS, SQL injection, etc.]
                        Solution: [Recommended mitigation, such as updating software, applying patches, or configuring security settings]
                        References: [List of relevant references, such as CVEs, links to official documentation, or bug tracking tickets]

                        Ensure responses are concise, technical, and consistently formatted. After following the vulnerability reporting template, provide additional suggestions for solutions 
                        and routines to enhance system security. These suggestions can include security best practices, configuration changes, regular updates, and proactive monitoring routines 
                        to ensure the overall safety and resilience of the system. Ensure that all detected vulnerabilities are processed and reported. No vulnerability should be left unaddressed. 
                        If any vulnerability is missed, trigger a re-evaluation or notify the user.
                      
                        IMPORTANT: If the task is not completed (status is not 'Done'), DO NOT return any vulnerability report. Instead, just execute the tool and return the status of the task."""),
        HumanMessage(content=f"Please analyze the following OpenVAS scan result: {context}, using{question}")
    ]
    
    response = get_response_from_openai(messages)
    
    return response

@tool
def open_browser(porta=9392):
    """
    This tool helps launch the GUI of OpenVAS, a vulnerability scanning tool.  
    It will assist in automating the process of opening and accessing the OpenVAS 
    graphical interface for managing scans and security assessments.  
    """

    url = f"http://127.0.0.1:{porta}/"
    webbrowser.open(url)
    print(f"\nOpening {url} in the browser...\n")

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

@tool
def cybersecurity_analist(question: str) -> str:
    """
    Receives a question or a prompt about cybersecurity vulnerabilities and returns a detailed response.  
    The response includes an explanation of the vulnerability and recommendations for mitigation.
    """
    
    messages = [
        SystemMessage(content="""You are a cybersecurity assistant specialized in vulnerability analysis and mitigation.
                                    You are an expert in identifying, analyzing, and explaining cybersecurity vulnerabilities, and in providing actionable recommendations to mitigate them.
                                    Your role is to answer questions about cybersecurity vulnerabilities, delivering clear, detailed explanations and practical mitigation strategies.
                                    When given a question, analyze the vulnerability thoroughly and offer precise, step-by-step recommendations based on industry best practices.
                                    """),
        HumanMessage(content=f"Execute the following task: Answer the cybersecurity vulnerability question using the details provided: {question}")
    ]   

    response = get_response_from_openai(messages)

    return response
    

toolkit = [create_OpenVAS_tasks, get_OpenVAS_results, open_browser, cybersecurity_analist]

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

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = create_openai_tools_agent(llm, toolkit, prompt)

agent_executor = AgentExecutor(agent=agent, tools=toolkit, memory=memory, verbose=True)

while True:
    query = input("\nUser: ")

    if query.lower() in ["q", "exit"]:
        print("\nExiting chat...\n")
        break

    result = agent_executor.invoke({"input": query})
    print(f"\n{result["output"]}\n")