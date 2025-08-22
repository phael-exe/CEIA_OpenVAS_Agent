import functools
import re
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from ..tools.gvm_workflow import GVMWorkflow
from ..state import AgentState  # Import AgentState

@tool
def create_openvas_task(question: str) -> str:
    """Cria e inicia uma nova tarefa de scan de vulnerabilidade no OpenVAS para um IP específico."""
    
    # Extrai o IP da pergunta usando regex
    target_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:-[0-9]{1,3})?\b|\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\b'
    match = re.search(target_pattern, question)
    
    if not match:
        return "Error: No IP address, IP range, or hostname found in the question. Please specify a target (e.g., 'create task for 192.168.1.1', 'create task for 192.168.1.1-255', or 'create task for example.com')."
        
    target_host = match.group(0)

    # Extrai o nome da tarefa da pergunta usando regex
    task_name_pattern = r"""(?:called|name)\s+["']([^'"]+)[""]"""
    task_name_match = re.search(task_name_pattern, question, re.IGNORECASE)
    
    if task_name_match:
        task_name = task_name_match.group(1)
    else:
        task_name = f"Automated Scan for {target_host}"

    try:
        workflow = GVMWorkflow()
        result = workflow.run(task_name, target_host)
        return f"\nTool 'create_openvas_task' executed successfully. {result}"
    except Exception as e:
        return f"\nError executing tool 'create_openvas_task': {e}"

def create_task_creator_node():
    """Cria o nó do agente criador de tarefas."""
    return functools.partial(tool_node, tool_to_run=create_openvas_task)

def tool_node(state: AgentState, tool_to_run: callable) -> dict:
    """Função genérica para executar um nó de ferramenta."""
    last_message = state['messages'][-1]
    tool_input = {"question": last_message.content}
    result = tool_to_run.invoke(tool_input)
    return {"messages": [ToolMessage(content=str(result), tool_call_id="tool_node_call")]}