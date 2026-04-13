from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from typing import List, Any

# Available Groq models
GROQ_MODELS = {
    "fast": "llama-3.1-8b-instant",   # Speed model (FLASH equivalent)
    "quality": "llama-3.3-70b-versatile",  # Quality model (PRO equivalent)
}

class RAGChainManager:
    def __init__(self, model_name: str = GROQ_MODELS["fast"]):
        self.default_model_name = model_name
        self.prompt = PromptTemplate(
            template="""You are a helpful assistant.
Answer ONLY from the provided transcript context.
If the context is insufficient, just say "I don't know based on the video content."

Context: {context}
Question: {question}

Answer:""",
            input_variables=["context", "question"]
        )
        self.parser = StrOutputParser()

    def _get_model(self, model_name: str = None) -> ChatGroq:
        return ChatGroq(
            model=model_name or self.default_model_name,
            temperature=0.2,
        )

    @staticmethod
    def format_docs(retrieved_docs) -> str:
        return "\n\n".join(doc.page_content for doc in retrieved_docs)

    def get_chain(self, retriever, model_name: str = None):
        """
        Returns a RunnableParallel chain that outputs {'answer': str, 'docs': list}.
        Supports real-time streaming of the 'answer' field.
        """
        model = self._get_model(model_name)

        answer_chain = (
            RunnablePassthrough.assign(
                context=lambda x: self.format_docs(x["docs"])
            )
            | self.prompt
            | model
            | self.parser
        )

        return RunnableParallel({
            "answer": answer_chain,
            "docs": lambda x: x["docs"]
        })

    async def generate_title(self, chunks: List[Any]) -> str:
        """
        Generates a 3-5 word catchy title for a session based on transcript chunks.
        Falls back to a generic title if generation fails.
        """
        try:
            model = self._get_model(GROQ_MODELS["fast"])
            context = "\n".join([c.page_content for c in chunks[:3]])
            prompt = f"""Based on this YouTube video transcript snippet, generate a catchy 3-5 word title for a chat session.
Snippet: {context}

Respond with ONLY the title. No quotes, no prefix, no explanation."""
            response = await model.ainvoke(prompt)
            title = response.content.strip()
            # Safety: cap length to avoid abnormally long titles
            return title[:60] if title else "Untitled Session"
        except Exception:
            return "Untitled Session"
