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
        Preserves segment-level metadata (timestamps).
        """
        video_id = self.extract_video_id(url)
        try:
            api = youtube_transcript_api.YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            
            # Create a list of documents, one for each segment
            # This ensures that when we split, each chunk retains the timestamp metadata
            documents = [
                Document(
                    page_content=item.text,
                    metadata={
                        "source": video_id, 
                        "url": url,
                        "start": item.start,
                        "duration": item.duration
                    }
                )
                for item in transcript_list
            ]
            
            # Split into chunks (LangChain splitters preserve metadata)
            chunks = self.splitter.split_documents(documents)
            return chunks
        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")

    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """
        Returns basic metadata.
        """
        video_id = self.extract_video_id(url)
        return {
            "title": f"Video {video_id}", 
            "author": "YouTube Content", 
            "video_id": video_id
        }
