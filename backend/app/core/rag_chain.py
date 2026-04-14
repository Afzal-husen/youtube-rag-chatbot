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
            template="""You are a world-class insights assistant analyzing a YouTube video transcript.
Use the provided transcript context to answer the user's question in a helpful and detailed manner.
If the context does not contain the answer, you can briefly use your general knowledge but MUST clearly state that the information was NOT found in the video.

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
        Returns a chain that retrieves docs and generates an answer.
        Input: str (the question)
        Output: dict {'answer': str, 'docs': list}
        """
        model = self._get_model(model_name)

        # 1. Retrieval + Question Passthrough
        setup_and_retrieval = RunnableParallel({
            "docs": retriever,
            "question": RunnablePassthrough()
        })

        # 2. Answer Generation
        answer_chain = (
            RunnablePassthrough.assign(
                context=lambda x: self.format_docs(x["docs"])
            )
            | self.prompt
            | model
            | self.parser
        )

        # 3. Final Parallel Output
        return setup_and_retrieval | RunnableParallel({
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
