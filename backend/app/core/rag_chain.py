from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from typing import List, Dict, Any

class RAGChainManager:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.default_model_name = model_name
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

    def _get_model(self, model_name: str = None):
        return ChatGoogleGenerativeAI(model=model_name or self.default_model_name)

    @staticmethod
    def format_docs(retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)

    def get_chain(self, retriever, model_name: str = None):
        """
        Returns a chain that outputs a dictionary containing 'answer' and 'docs'.
        Supports real-time streaming of the 'answer' field.
        """
        model = self._get_model(model_name)
        
        # Step 1: Retrieval + Question preservation
        map_chain = RunnableParallel({
            "docs": retriever,
            "question": RunnablePassthrough()
        })
        
        # Step 2: Answer generation and results collection
        answer_chain = (
            RunnablePassthrough.assign(
                context=lambda x: self.format_docs(x["docs"])
            )
            | self.prompt
            | model
            | self.parser
        )

        # Final chain returns both the answer and the documents
        return RunnableParallel({
            "answer": answer_chain,
            "docs": lambda x: x["docs"]
        })

    async def generate_title(self, chunks: List[Any]) -> str:
        """
        Generates a 3-5 word catchy title based on the first few chunks of the transcript.
        """
        model = self._get_model()
        # Take first 3 chunks to understand context
        context = "\n".join([c.page_content for c in chunks[:3]])
        
        prompt = f"""
        Based on the following YouTube video transcript snippet, generate a catchy, 3-5 word title for the chat session.
        Snippet: {context}
        
        Respond ONLY with the generated title. No quotes, no prefix.
        """
        
        response = await model.ainvoke(prompt)
        return response.content.strip()
