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

# Importações das suas ferramentas
from src.tools.gvm_workflow import GVMWorkflow
from src.tools.gvm_results import ResultManager
from src.art.art import art_main

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Ferramentas ---

def get_response_from_openai(message):

    llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature=0.1,
        max_completion_tokens=None,
        timeout=None,
        )
    
    response = llm.invoke(message)
    
    return response

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL_ID"), temperature=0)

@tool
def create_openvas_task(question: str) -> str:
    """Cria e inicia uma nova tarefa de varredura de vulnerabilidades no OpenVAS."""
    print("--- EXECUTANDO A FERRAMENTA: create_openvas_task ---")
    try:
        workflow = GVMWorkflow()
        result = workflow.run()
        # Garante que sempre retornamos uma string para o LLM
        return f"Ferramenta 'create_openvas_task' executada com sucesso. Resultado: {str(result)}"
    except Exception as e:
        return f"Erro ao executar a ferramenta 'create_openvas_task': {e}"

@tool
def get_openvas_results(question: str) -> str:
    """Busca e analisa os resultados de uma varredura de vulnerabilidades do OpenVAS."""
    print("--- EXECUTANDO A FERRAMENTA: get_openvas_results ---")
    try:
        result_manager = ResultManager()
        context = result_manager.result()
        messages = [
            SystemMessage(content="""You are a cybersecurity assistant specializing in network scanning 
                      and penetration testing. With expert knowledge of OpenVAS, a powerful vulnerability 
                      scanning tool, your role is to interpret everything that comes within context and provide
                      to the user with insights on how to resolve each vulnerability.  
                      
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
        return f"Erro ao executar a ferramenta 'get_openvas_results': {e}"


# --- Estrutura Multiagente ---

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def tool_node(state: AgentState, tool_to_run: callable) -> dict:
    last_message = state['messages'][-1]
    tool_input = {"question": last_message.content}
    result = tool_to_run.invoke(tool_input)
    return {"messages": [ToolMessage(content=str(result), tool_call_id="tool_node_call")]}

task_creator_node = functools.partial(tool_node, tool_to_run=create_openvas_task)
result_analyzer_node = functools.partial(tool_node, tool_to_run=get_openvas_results)

# --- Supervisor com Saída Estruturada ---

class Route(BaseModel):
    """Define a rota para o próximo passo."""
    next: Literal["TaskCreator", "ResultAnalyzer", "FINISH"] = Field(
        ...,
        description="A rota para o próximo trabalhador ou 'FINISH' para encerrar."
    )

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL_ID"), temperature=0)
structured_llm_router = llm.with_structured_output(Route)

system_prompt_supervisor = (
    "Você é um supervisor especialista em OpenVAS. Analise a conversa e decida o próximo passo.\n"
    " - Se o usuário quer CRIAR, INICIAR ou EXECUTAR uma varredura, o próximo passo é 'TaskCreator'.\n"
    " - Se o usuário quer ANALISAR, VER, OBTER ou BUSCAR resultados, o próximo passo é 'ResultAnalyzer'.\n"
    " - Se a intenção não é clara, o próximo passo é 'FINISH'."
)

prompt_supervisor = ChatPromptTemplate.from_messages([
    ("system", system_prompt_supervisor),
    MessagesPlaceholder(variable_name="messages"),
])

supervisor_chain = prompt_supervisor | structured_llm_router

### MUDANÇA PRINCIPAL: Lógica de Roteamento Robusta ###
def router_function(state: AgentState):
    """
    Decide o próximo passo. Se uma ferramenta acabou de rodar, finaliza.
    Caso contrário, pergunta ao supervisor.
    """
    print("--- Decisão do Supervisor ---")

    # Verifica se a última mensagem é o resultado de uma ferramenta.
    # Se for, o trabalho do agente terminou e o ciclo deve ser finalizado.
    if isinstance(state['messages'][-1], ToolMessage):
        print("Trabalho do agente concluído. Finalizando.")
        return "FINISH"

    # Se não, é a primeira chamada. Pergunta ao LLM qual rota seguir.
    route_decision = supervisor_chain.invoke(state)
    print(f"Próximo passo decidido: {route_decision.next}")
    return route_decision.next


# --- Construção do Grafo ---
workflow = StateGraph(AgentState)

workflow.add_node("TaskCreator", task_creator_node)
workflow.add_node("ResultAnalyzer", result_analyzer_node)
# O nó supervisor não faz nada por si só, apenas serve como ponto de roteamento
workflow.add_node("supervisor", lambda state: {"messages": []})

# As arestas de volta para o supervisor
workflow.add_edge("TaskCreator", "supervisor")
workflow.add_edge("ResultAnalyzer", "supervisor")

# Roteamento condicional a partir do supervisor
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

# --- Loop Principal de Interação ---
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERRO: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    else:
        art_main()
        while True:
            query = input("\nUser: ")
            if query.lower() in ["q", "exit", "quit", "sair"]:
                print("\nSaindo...")
                break

            initial_state = {"messages": [HumanMessage(content=query)]}

            try:
                print("\n--- Início do Fluxo ---")
                final_state = graph.invoke(initial_state, {"recursion_limit": 5})
                print("\n--- Fim do Fluxo ---")
                final_message = final_state['messages'][-1]
                print(f"\nResultado Final: {final_message.content}")


            except Exception as e:
                import traceback
                print(f"\n--- Ocorreu um Erro Inesperado ---")
                traceback.print_exc()
                print("------------------------------------\n")