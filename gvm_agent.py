import os
from dotenv import load_dotenv
from gvm_workflow import GVMWorkflow


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
        temperature=0.2,
        max_completion_tokens=None,
        timeout=None,
        api_key=api_key,
        )
    
    response = llm.invoke(message)
    
    return response

@tool
def create_OpenVAS_task(question: str):
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

toolkit = [create_OpenVAS_task]

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
                        If you don't have a tool to answer the question, say no.
                        
                        Return only a message with the task created.
         """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
        
    ]
)

agent = create_openai_tools_agent(llm, toolkit, prompt)

agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=True)

result = agent_executor.invoke({"input":"Create a task in OpenVAS to scan a specific target."})

print(result["output"])