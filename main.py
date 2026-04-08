from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, FetchedTranscript
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

video_id = "Gfr50f6ZBvo"

transcription_api = YouTubeTranscriptApi()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")


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

chunks = splitter.create_documents(texts=transcription)

vector_store = FAISS.from_documents(documents=chunks[:100], embedding=embedding)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

result = retriever.invoke("what is deepmind ?")

for doc in result:
    print(doc.page_content)