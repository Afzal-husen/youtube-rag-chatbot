from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from typing import List

class RAGChainManager:
    def __init__(self, model_name: str = "gemini-flash-latest"):
        self.model = ChatGoogleGenerativeAI(model=model_name)
        self.prompt = PromptTemplate(
            template="""
            You are a helpful assistant.
            Answer ONLY from the provided transcript context.
            If the context is insufficient, just say "I don't know".
            
            Context: {context}
            Question: {question}
            """,
            input_variables=["context", "question"]
        )
        self.parser = StrOutputParser()

    @staticmethod
    def format_docs(retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)

    def get_chain(self, retriever):
        parallel_chain = RunnableParallel({
            "context": retriever | RunnableLambda(self.format_docs),
            "question": RunnablePassthrough()
        })
        
        return parallel_chain | self.prompt | self.model | self.parser
