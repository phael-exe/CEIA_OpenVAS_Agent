import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class LLM:
    def __init__(self) -> None:
        self.__api_key = os.getenv("OPENAI_API_KEY")

        if not self.__api_key:
            raise ValueError("API key is not found. Check your .env file.")
        
    def connect_openai(self):

        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_completion_tokens=None,
            timeout=None,
            api_key=self.__api_key
        )
    
if __name__ == "__main__":
    llm = LLM()
    chat_model = llm.connect_openai()
    print("Connection sucessfully:", chat_model)