from typing import Literal
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..state import AgentState

class Route(BaseModel):
    """Defines the route for the agent."""
    next: Literal["TaskCreator", "ResultAnalyzer", "CSVAnalyzer"] = Field(
        ...,
        description="The route to the next worker or 'FINISH' to end.")
    
def create_supervisor_chain(llm: ChatOpenAI):
    """Cria a cadeia de decisão do supervisor."""
    system_prompt_supervisor = (
        """You are an expert OpenVAS supervisor and a helpful assistant. Your primary goal is to assist the user with OpenVAS tasks (creating scans, analyzing results, analyzing CSV reports) and also to provide general information and advice related to cybersecurity and vulnerability mitigation based on your knowledge.

Analyze the conversation and decide the next step:
 - If the user wants to CREATE, START, or RUN a scan, the next step is 'TaskCreator'.
 - If the user wants to ANALYZE, VIEW, GET, or FETCH results from OpenVAS directly, the next step is 'ResultAnalyzer'.
 - If the user wants to ANALYZE CSV, LIST CSV, READ CSV files, or work with CSV reports, the next step is 'CSVAnalyzer'.
 - If the intent is not clear, or the user is asking a general question about cybersecurity, vulnerabilities, or mitigation, respond conversationally and then the next step is 'FINISH'.
 - If a tool has just been executed and the result is available, respond with the result and ask if the user needs anything else. If the user's subsequent response indicates they are done, the next step is 'FINISH'."""
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

    # Verifica se a última mensagem é o resultado de uma ferramenta.
    # Se sim, o trabalho do agente está concluído e o ciclo deve ser encerrado.
    if isinstance(state['messages'][-1], ToolMessage):
        return "FINISH"

    # Se não, é a primeira chamada. Pergunta ao LLM qual rota seguir.
    route_decision = supervisor_chain.invoke(state)
    return route_decision.next