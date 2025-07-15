import functools
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from ..tools.gvm_results import ResultManager
from ..state import AgentState  # Import AgentState

def get_response_from_openai(message: list[BaseMessage]):
    """Função para obter resposta do OpenAI."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=None, # Changed from max_completion_tokens
        timeout=None,
    )
    response = llm.invoke(message)
    return response

@tool
def get_openvas_results(question: str) -> str:
    """Busca e analisa os resultados de um scan de vulnerabilidade do OpenVAS."""
    print("\n--- EXECUTING TOOL: get_openvas_results ---")
    try:
        result_manager = ResultManager()
        context = result_manager.result()
        messages = [
            SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability scanning tool, your role is to interpret everything that comes within the context and provide the user with insights on how to resolve each vulnerability.  
                      
                      When responding, follow this template and replace the placeholders with the appropriate values:

                        Vulnerability: [Name of the vulnerability, usually from databases like CVE, descriptive and concise]

                        ID: [Unique identifier for the vulnerability within the reporting system]
                        Host: [IP address of the affected host, optionally including an identifier like "_gateway" or "web server"]
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

def create_result_analyzer_node():
    """Cria o nó do agente analisador de resultados."""
    return functools.partial(tool_node, tool_to_run=get_openvas_results)

def tool_node(state: AgentState, tool_to_run: callable) -> dict:
    """Função genérica para executar um nó de ferramenta."""
    last_message = state['messages'][-1]
    tool_input = {"question": last_message.content}
    result = tool_to_run.invoke(tool_input)
    return {"messages": [ToolMessage(content=str(result), tool_call_id="tool_node_call")]}