import os
import sys
import time

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

try:
    log("Starting granular import test...")
    
    log("Importing fastapi...")
    import fastapi
    
    log("Importing sqlalchemy...")
    import sqlalchemy
    
    log("Importing langchain components (core)...")
    from langchain_core.prompts import PromptTemplate
    
    log("Importing langchain-google-genai...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    log("Importing langchain-huggingface (This might be slow)...")
    from langchain_huggingface import HuggingFaceEmbeddings
    
    log("Importing app layers...")
    log("Importing app.core.database...")
    import app.core.database
    
    log("Importing app.core.db_models...")
    import app.core.db_models
    
    log("Importing app.core.vector_store (The probable hang spot)...")
    import app.core.vector_store
    
    log("Importing app.core.rag_chain...")
    import app.core.rag_chain
    
    log("Importing app.api.endpoints (This triggers global instantiations)...")
    import app.api.endpoints
    
    log("Import successful!")

except Exception as e:
    log(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
