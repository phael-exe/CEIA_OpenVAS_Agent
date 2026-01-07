import os
import operator
from typing import TypedDict, Annotated, Sequence

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# Imports dos seus novos módulos de agentes
from src.agents.supervisor import create_supervisor_chain, router_function
from src.agents.task_creator import create_task_creator_node
from src.agents.result_analyzer import create_result_analyzer_node
from src.agents.csv_analyzer import create_csv_analyzer_node
from src.art.art import art_main
from src.state import AgentState

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# --- Inicialização do LLM ---
# Suporta tanto OpenAI quanto Groq
llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

if llm_provider == "groq":
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile"),
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
else:
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini"), temperature=0)

# --- Construção do Grafo ---
workflow = StateGraph(AgentState)

# Nós dos agentes
task_creator_node = create_task_creator_node()
result_analyzer_node = create_result_analyzer_node()
csv_analyzer_node = create_csv_analyzer_node()

workflow.add_node("TaskCreator", task_creator_node)
workflow.add_node("ResultAnalyzer", result_analyzer_node)
workflow.add_node("CSVAnalyzer", csv_analyzer_node)
workflow.add_node("supervisor", lambda state: {"messages": []}) # Nó supervisor vazio

# Edges de volta para o supervisor
workflow.add_edge("TaskCreator", "supervisor")
workflow.add_edge("ResultAnalyzer", "supervisor")
workflow.add_edge("CSVAnalyzer", "supervisor")

# Roteamento condicional do supervisor
supervisor_chain = create_supervisor_chain(llm)
workflow.add_conditional_edges(
    "supervisor",
    lambda state: router_function(state, supervisor_chain),
    {
        "TaskCreator": "TaskCreator",
        "ResultAnalyzer": "ResultAnalyzer",
        "CSVAnalyzer": "CSVAnalyzer",
        "FINISH": END,
        "supervisor": "supervisor",
    },
)

workflow.set_entry_point("supervisor")
graph = workflow.compile()

# --- Loop de Interação Principal ---
if __name__ == "__main__":
    # Verifica API key baseado no provider
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if llm_provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            print("Error: GROQ_API_KEY not found in environment variables.")
            print("Get your free key at: https://console.groq.com")
            exit(1)
    else:
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not found in environment variables.")
            exit(1)
    
    art_main()
    print(f"\n🤖 Using {llm_provider.upper()} as LLM provider")
    
    while True:
        query = input("\nUser: ")
        if query.lower() in ["q", "exit", "quit", "sair"]:
            print("\nExiting...")
            break

        initial_state = {"messages": [HumanMessage(content=query)]}

        try:
            print("Processing...")
            final_state = graph.invoke(initial_state, {"recursion_limit": 5})
            final_message = final_state['messages'][-1]
            print(f"\nResult: {final_message.content}")
            print("\nDo you need anything else?")

        except Exception as e:
            import traceback
            print(f"\n--- An Unexpected Error Occurred ---")
            traceback.print_exc()
            print("------------------------------------\n")