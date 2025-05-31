from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from pinecone import Pinecone
import os
import hashlib

# Load environment variables from .env file
load_dotenv()

# Pydantic models for request/response
class InfluencerData(BaseModel):
    username: str
    email: str
    bio: str
    followers: int
    posts: int

class InfluencerResponse(BaseModel):
    id: str
    username: str
    email: str
    bio: str
    followers: int
    posts: int

class QueryRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=50, description="Number of results to return (1-50)")

class PushInfluencersRequest(BaseModel):
    influencers: List[InfluencerData]

class QueryResponse(BaseModel):
    influencers: List[InfluencerResponse]
    count: int

# Initialize FastAPI app
app = FastAPI(
    title="Influencer Matching API",
    description="AI-powered influencer matching service using vector search",
    version="1.0.0"
)

def generate_deterministic_id(data):
    unique_str = data['username'] + data['email']
    return hashlib.md5(unique_str.encode()).hexdigest()

class AI_Matcher:
    def __init__(self):
        try:
            # Initialize Google Generative AI
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize the Pinecone client
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI Matcher: {str(e)}")

    def pineconeIndex_init(self):
        index_name = "influencer-matching"

        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            # Check if the index exists
            if not pc.has_index(index_name):
                raise HTTPException(status_code=404, detail=f"Index '{index_name}' does not exist.")

            # Connect to the existing index
            index = pc.Index(index_name)
            return index
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize Pinecone index: {str(e)}")

    def push_influencer(self, influencer_data):
        try:
            index = self.pineconeIndex_init()
            docs = []

            for data in influencer_data:
                summary = f"bio: {data['bio']}, username: {data['username']}, followers: {data['followers']}, posts: {data['posts']}"
                doc = Document(
                    page_content=summary,
                    metadata={
                        'username': data['username'],
                        'followers': data['followers'],
                        'posts': data['posts'],
                        'email': data['email'],
                        'bio': data['bio'],
                    }
                )
                docs.append(doc)

            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
            
            # This will auto-generate document IDs
            ids = [generate_deterministic_id(data) for data in influencer_data]
            vectorstore.add_documents(documents=docs, ids=ids)
            return len(docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to push influencers: {str(e)}")
    
    def query_influencer(self, query, k):
        try:
            ## Query top k influencers based on the query and return their details with id 
            index = self.pineconeIndex_init()
            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
            results = vectorstore.similarity_search(query, k=k)
            influencers = []
            for result in results:
                influencer = {
                    'id': result.id if hasattr(result, 'id') else generate_deterministic_id({
                        'username': result.metadata['username'],
                        'email': result.metadata['email']
                    }),
                    'username': result.metadata['username'],
                    'followers': result.metadata['followers'],
                    'posts': result.metadata['posts'],
                    'email': result.metadata['email'],
                    'bio': result.metadata['bio']
                }
                influencers.append(influencer)
            return influencers
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to query influencers: {str(e)}")

# Initialize AI Matcher instance
ai_matcher = AI_Matcher()

@app.get("/")
async def root():
    return {
        "message": "Influencer Matching API",
        "version": "1.0.0",
        "endpoints": {
            "push_influencers": "/influencers/push",
            "query_influencers": "/influencers/query",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Matcher is running"}

@app.post("/influencers/push", response_model=dict)
async def push_influencers(request: PushInfluencersRequest):
    """
    Push influencer data to the vector database
    """
    try:
        # Convert Pydantic models to dict
        influencer_data = [influencer.dict() for influencer in request.influencers]
        count = ai_matcher.push_influencer(influencer_data)
        return {
            "message": f"Successfully pushed {count} influencers",
            "count": count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/influencers/query", response_model=QueryResponse)
async def query_influencers(request: QueryRequest):
    """
    Query influencers based on search criteria
    """
    try:
        influencers = ai_matcher.query_influencer(request.query, request.k)
        return QueryResponse(
            influencers=influencers,
            count=len(influencers)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/influencers/search/{query}")
async def search_influencers_get(query: str, k: int = 5):
    """
    Alternative GET endpoint for searching influencers (for simple queries)
    """
    if k < 1 or k > 50:
        raise HTTPException(status_code=400, detail="k must be between 1 and 50")
    
    try:
        influencers = ai_matcher.query_influencer(query, k)
        return QueryResponse(
            influencers=influencers,
            count=len(influencers)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

    # Start Commands:
    # python app.py
    # # or
    # uvicorn app:app --host 0.0.0.0 --port 8000 --reload