import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Representa o estado do nosso agente.

    Attributes:
        messages: Uma sequência de mensagens que se acumulam ao longo do tempo.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]