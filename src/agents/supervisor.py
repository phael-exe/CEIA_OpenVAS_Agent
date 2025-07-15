from typing import Literal
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..state import AgentState

class Route(BaseModel):
    """Defines the route for the agent."""
    next: Literal["TaskCreator", "ResultAnalyzer"] = Field(
        ...,
        description="The route to the next worker or 'FINISH' to end.")
    
def create_supervisor_chain(llm: ChatOpenAI):
    """Cria a cadeia de decisão do supervisor."""
    system_prompt_supervisor = (
        "You are an expert OpenVAS supervisor. Analyze the conversation and decide the next step.\n"
        " - If the user wants to CREATE, START, or RUN a scan, the next step is 'TaskCreator'.\n"
        " - If the user wants to ANALYZE, VIEW, GET, or FETCH results, the next step is 'ResultAnalyzer'.\n"
        " - If the intent is not clear, the next step is 'FINISH'."
    )

    prompt_supervisor = ChatPromptTemplate.from_messages([
        ("system", system_prompt_supervisor),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    structured_llm_router = llm.with_structured_output(Route)
    return prompt_supervisor | structured_llm_router

def router_function(state: AgentState, supervisor_chain):
    """
    Decide o próximo passo. Se uma ferramenta acabou de ser executada, finaliza.
    Caso contrário, pergunta ao supervisor.
    """
    print("\n--- Supervisor Decision ---")

    # Verifica se a última mensagem é o resultado de uma ferramenta.
    # Se sim, o trabalho do agente está concluído e o ciclo deve ser encerrado.
    if isinstance(state['messages'][-1], ToolMessage):
        print("\nAgent work completed. Finalizing.")
        return "FINISH"

    # Se não, é a primeira chamada. Pergunta ao LLM qual rota seguir.
    route_decision = supervisor_chain.invoke(state)
    print(f"\nNext step decided: {route_decision.next}")
    return route_decision.next