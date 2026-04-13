from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, FetchedTranscript
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
import os

load_dotenv()

os.environ["HF_HOME"] = "D:/huggingface_cache"

video_id = "C6ioLFXAMVE"

transcription_api = YouTubeTranscriptApi()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000*0.15)
embedding = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")


try:
    transcription_list = transcription_api.fetch(
        video_id=video_id,
        languages=["en"]
    )
except TranscriptsDisabled:
    print("No caption available for the video")

def format_transcription(transcription_list: FetchedTranscript):
    text_list = []
    for chunk in transcription_list:
        text_list.append(chunk.text)
    return " ".join(text_list)

transcription = format_transcription(transcription_list)

# print(transcription)



splitted_text = splitter.split_text(text=transcription)

chunks = splitter.create_documents(texts=splitted_text)

vector_store = FAISS.from_documents(documents=chunks, embedding=embedding)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

question = "what does the video talk about?"

def format_docs(retrieved_docs):
    retrieved_context = []

    for doc in retrieved_docs:
        retrieved_context.append(doc.page_content)
    return " ".join(retrieved_context)


parallel_chain = RunnableParallel({
    "context": retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})



prompt = PromptTemplate(
    template="""
    You are a helpfull assistant.
    answer ONLY from the provided transcript context.
    if context is insufficient, then just say I don't know.
    
    {context}
    question: {question}
    """,
    input_variables=["context", "question"]
)

model = ChatGroq(model="openai/gpt-oss-20b")

parser = StrOutputParser()

chain = parallel_chain | prompt | model | parser

while True:
    user_input = input("question: ")
    result = chain.invoke(user_input)
    print(result)



