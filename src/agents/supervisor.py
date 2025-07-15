from typing import Literal
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ...main import AgentState

class Route(BaseModel):
    """Defines the route for the agent."""
    next: Literal["TaskCreator", "ResultAnalyzer"] = Field(
        ...,
        description="A rota para o próximo worker ou 'FINISH' para terminar.")
    
def create_supervisor_chain(llm: ChatOpenAI):
    """Cria a cadeia de decisão do supervisor."""
    system_prompt_supervisor = (
        "Você é um supervisor especialista em OpenVAS. Analise a conversa e decida o próximo passo.\n"
        " - Se o usuário quiser CRIAR, INICIAR ou EXECUTAR um scan, o próximo passo é 'TaskCreator'.\n"
        " - Se o usuário quiser ANALISAR, VER, OBTER ou BUSCAR resultados, o próximo passo é 'ResultAnalyzer'.\n"
        " - Se a intenção não for clara, o próximo passo é 'FINISH'."
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
    print("\n--- Decisão do Supervisor ---")

    # Verifica se a última mensagem é o resultado de uma ferramenta.
    # Se sim, o trabalho do agente está concluído e o ciclo deve ser encerrado.
    if isinstance(state['messages'][-1], ToolMessage):
        print("\nTrabalho do agente concluído. Finalizando.")
        return "FINISH"

    # Se não, é a primeira chamada. Pergunta ao LLM qual rota seguir.
    route_decision = supervisor_chain.invoke(state)
    print(f"\nPróximo passo decidido: {route_decision.next}")
    return route_decision.next