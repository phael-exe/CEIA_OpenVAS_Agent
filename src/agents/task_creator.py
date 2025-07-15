import functools
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from ..tools.gvm_workflow import GVMWorkflow
from ..state import AgentState  # Import AgentState
@tool
def create_openvas_task(question: str) -> str:
    """Cria e inicia uma nova tarefa de scan de vulnerabilidade no OpenVAS."""
    print("\n--- EXECUTING THE TOOL: create_openvas_task ---")
    try:
        workflow = GVMWorkflow()
        result = workflow.run()
        # Garante que sempre retornemos uma string para o LLM
        return f"\nTool 'create_openvas_task' executed successfully. Result: {str(result)}"
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