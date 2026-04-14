import os
import shutil
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreManager:
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.storage_path = os.path.join(backend_dir, "storage")
        else:
            self.storage_path = storage_path
        
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            print("Initializing HuggingFaceEmbeddings (First load)...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                cache_folder=os.environ.get("HF_HOME", "D:/huggingface_cache")
            )
        return self._embeddings

    def get_index_path(self, video_id: str) -> str:
        """
        Returns the path to the FAISS index for a specific video.
        """
        # Sanitize video_id to ensure filesystem compatibility
        clean_id = "".join([c for c in video_id if c.isalnum() or c in ("-", "_")])
        return os.path.join(self.storage_path, f"faiss_{clean_id}")

    def index_exists(self, video_id: str) -> bool:
        """
        Checks if a local index already exists for the video.
        """
        path = self.get_index_path(video_id)
        return os.path.exists(path)

    def load_index(self, video_id: str) -> Optional[FAISS]:
        """
        Loads a local FAISS index.
        """
        if not self.index_exists(video_id):
            return None
        
        path = self.get_index_path(video_id)
        return FAISS.load_local(
            path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

    def create_and_save_index(self, video_id: str, documents) -> FAISS:
        """
        Creates a new FAISS index and saves it to disk.
        """
        vector_store = FAISS.from_documents(documents, self.embeddings)
        path = self.get_index_path(video_id)
        vector_store.save_local(path)
        return vector_store

    def delete_index(self, video_id: str):
        """
        Physically removes the FAISS index directory from disk.
        """
        path = self.get_index_path(video_id)
        if os.path.exists(path):
            shutil.rmtree(path)
