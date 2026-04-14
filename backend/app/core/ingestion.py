from typing import List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class IngestionManager:
    def __init__(self, chunk_size: int = 1000, chunk_overlap_ratio: float = 0.15):
        self.chunk_size = chunk_size
        self.chunk_overlap = int(chunk_size * chunk_overlap_ratio)

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
        Loads and groups transcript segments into larger, overlapping chunks.
        This provides much better context for the RAG LLM than individual segments.
        """
        video_id = self.extract_video_id(url)
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            
            chunks = []
            current_text = ""
            current_start = None
            
            for segment in transcript_list:
                if current_start is None:
                    current_start = segment.start
                
                current_text += segment.text + " "
                
                # If we've accumulated enough text, create a chunk
                if len(current_text) >= self.chunk_size:
                    chunks.append(Document(
                        page_content=current_text.strip(),
                        metadata={
                            "source": video_id, 
                            "url": url,
                            "start": current_start,
                            "duration": segment.start + segment.duration - current_start
                        }
                    ))
                    # Handle overlap: keep a portion of the end for the next chunk
                    current_text = current_text[-self.chunk_overlap:]
                    # Reset start time (it will be set by the next segment in the loop)
                    current_start = None 

            # Add the final partial chunk if any
            if current_text.strip():
                chunks.append(Document(
                    page_content=current_text.strip(),
                    metadata={
                        "source": video_id,
                        "url": url,
                        "start": current_start or 0.0,
                        "duration": transcript_list[-1].start + transcript_list[-1].duration - (current_start or 0.0)
                    }
                ))

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
