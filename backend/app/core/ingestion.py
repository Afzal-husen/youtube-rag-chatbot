from typing import List, Dict, Any
import youtube_transcript_api
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class IngestionManager:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )

    @staticmethod
    def extract_video_id(url: str) -> str:
        """
        Extracts the video ID from a YouTube URL.
        """
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "be/" in url:
            return url.split("be/")[1].split("?")[0]
        return url

    def load_and_split(self, url: str) -> List[Document]:
        """
        Loads the transcript for a video and splits it into chunks.
        """
        video_id = self.extract_video_id(url)
        try:
            api = youtube_transcript_api.YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            full_text = " ".join([item.text for item in transcript_list])
            
            # Create a LangChain document
            doc = Document(
                page_content=full_text,
                metadata={"source": video_id, "url": url}
            )
            
            # Split into chunks
            chunks = self.splitter.split_documents([doc])
            return chunks
        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")

    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """
        Returns basic metadata (YouTube API v3 or scrapers would be needed for more).
        """
        video_id = self.extract_video_id(url)
        return {
            "title": f"Video {video_id}", 
            "author": "YouTube Content", 
            "video_id": video_id
        }
