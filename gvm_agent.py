# gvm_agent.py

import os
import functools
import operator
from typing import TypedDict, Annotated, Sequence, Literal

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Imports from your tools
from src.tools.gvm_workflow import GVMWorkflow
from src.tools.gvm_results import ResultManager
from src.art.art import art_main

# Loads environment variables from the .env file
load_dotenv()

# --- Tools ---

def get_response_from_openai(message):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        max_completion_tokens=None,
        timeout=None,
    )
    response = llm.invoke(message)
    return response

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL_ID"), temperature=0)

@tool
def create_openvas_task(question: str) -> str:
    """Creates and starts a new vulnerability scan task in OpenVAS."""
    print("\n--- EXECUTING TOOL: create_openvas_task ---")
    try:
        workflow = GVMWorkflow()
        result = workflow.run()
        # Ensures we always return a string to the LLM
        return f"\nTool 'create_openvas_task' executed successfully. Result: {str(result)}"
    except Exception as e:
        return f"\nError executing tool 'create_openvas_task': {e}"

@tool
def get_openvas_results(question: str) -> str:
    """Fetches and analyzes the results of an OpenVAS vulnerability scan."""
    print("\n--- EXECUTING TOOL: get_openvas_results ---")
    try:
        result_manager = ResultManager()
        context = result_manager.result()
        messages = [
            SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning 
                      and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability 
                      scanning tool, your role is to interpret everything that comes within context and provide
                      the user with insights on how to resolve each vulnerability.  
                      
                      When responding, follow this template and replace the placeholders with the appropriate values:

                        Vulnerability: [Name of the vulnerability, typically from databases like CVE, descriptive and concise]

                        ID: [Unique identifier for the vulnerability within the reporting system]
                        Host: _[IP address of the affected host, optionally including an identifier such as "_gateway" or "webserver"]
                        Port: [Affected port number and protocol (e.g., 443/tcp)]
                        CVSS Base Score: [Severity score based on the CVSS scale, indicating if it is low, medium, high, or critical]
                        Description: [Brief technical explanation of the vulnerability, including its cause and potential impacts, such as remote code execution, XSS, SQL injection, etc.]
                        Solution: [Recommended mitigation, such as updating software, applying patches, or configuring security settings]
                        References: [List of relevant references, such as CVEs, links to official documentation, or bug tracking tickets]"""),
            HumanMessage(content=f"Please analyze the following OpenVAS scan result: {context}, using {question}")
        ]
    
        response = get_response_from_openai(messages)
    
        return response.content
    except Exception as e:
        return f"\nError executing tool 'get_openvas_results': {e}"

# --- Multi-agent Structure ---

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def tool_node(state: AgentState, tool_to_run: callable) -> dict:
    last_message = state['messages'][-1]
    tool_input = {"question": last_message.content}
    result = tool_to_run.invoke(tool_input)
    return {"messages": [ToolMessage(content=str(result), tool_call_id="tool_node_call")]}

task_creator_node = functools.partial(tool_node, tool_to_run=create_openvas_task)
result_analyzer_node = functools.partial(tool_node, tool_to_run=get_openvas_results)

# --- Supervisor with Structured Output ---

class Route(BaseModel):
    """Defines the route for the next step."""
    next: Literal["TaskCreator", "ResultAnalyzer", "FINISH"] = Field(
        ...,
        description="The route to the next worker or 'FINISH' to end."
    )

structured_llm_router = llm.with_structured_output(Route)

system_prompt_supervisor = (
    "You are an OpenVAS expert supervisor. Analyze the conversation and decide the next step.\n"
    " - If the user wants to CREATE, START, or RUN a scan, the next step is 'TaskCreator'.\n"
    " - If the user wants to ANALYZE, VIEW, GET, or FETCH results, the next step is 'ResultAnalyzer'.\n"
    " - If the intent is unclear, the next step is 'FINISH'."
)

prompt_supervisor = ChatPromptTemplate.from_messages([
    ("system", system_prompt_supervisor),
    MessagesPlaceholder(variable_name="messages"),
])

supervisor_chain = prompt_supervisor | structured_llm_router

### MAIN CHANGE: Robust Routing Logic ###
def router_function(state: AgentState):
    """
    Decides the next step. If a tool has just run, it finishes. 
    Otherwise, it asks the supervisor.
    """
    print("\n--- Supervisor Decision ---")

    # Checks if the last message is the result of a tool.
    # If so, the agent's job is done and the cycle should be ended.
    if isinstance(state['messages'][-1], ToolMessage):
        print("\nAgent's job is complete. Finishing.")
        return "FINISH"

    # If not, it's the first call. Asks the LLM which route to take.
    route_decision = supervisor_chain.invoke(state)
    print(f"\nNext step decided: {route_decision.next}")
    return route_decision.next

# --- Graph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("TaskCreator", task_creator_node)
workflow.add_node("ResultAnalyzer", result_analyzer_node)
# The supervisor node does nothing on its own, it just serves as a routing point
workflow.add_node("supervisor", lambda state: {"messages": []})

# The edges back to the supervisor
workflow.add_edge("TaskCreator", "supervisor")
workflow.add_edge("ResultAnalyzer", "supervisor")

# Conditional routing from the supervisor
workflow.add_conditional_edges(
    "supervisor",
    router_function,
    {
        "TaskCreator": "TaskCreator",
        "ResultAnalyzer": "ResultAnalyzer",
        "FINISH": END,
    },
)

workflow.set_entry_point("supervisor")
graph = workflow.compile()

# --- Main Interaction Loop ---
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: The OPENAI_API_KEY environment variable was not found.")
    else:
        art_main()
        while True:
            query = input("\nUser: ")
            if query.lower() in ["q", "exit", "quit", "sair"]:
                print("\nExiting...")
                break

            initial_state = {"messages": [HumanMessage(content=query)]}

            try:
                print("\n--- Start of Flow ---")
                final_state = graph.invoke(initial_state, {"recursion_limit": 5})
                print("\n--- End of Flow ---")
                final_message = final_state['messages'][-1]
                print(f"\nFinal Result: {final_message.content}")

            except Exception as e:
                import traceback
                print(f"\n--- An Unexpected Error Occurred ---")
                traceback.print_exc()
                print("------------------------------------\n")