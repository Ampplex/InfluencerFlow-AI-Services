from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pinecone import Pinecone
import os
import hashlib
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate
import json
from mock_data import temp_influencer, influencers
import smtplib
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()

# Pydantic models for request/response
class InfluencerData(BaseModel):
    username: str
    email: str
    bio: str
    followers: int
    platform: str  # Added missing platform field
    link: Optional[str] = None

class InfluencerResponse(BaseModel):
    id: str
    username: str
    email: str
    bio: str
    followers: int
    platform: str  # Added missing platform field
    link: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=50, description="Number of results to return (1-50)")

class PushInfluencersRequest(BaseModel):
    influencers: List[InfluencerData]

class QueryResponse(BaseModel):
    influencers: List[InfluencerResponse]
    count: int

# Outreaching 
class OutreachData(BaseModel):
    influencers_data: List[Dict[str, Any]]
    brand_name: str = Field(..., description="Name of the brand for outreach email generation")
    brand_description: str = Field(..., description="Description of the brand for outreach email generation")
    campaign_id: str = Field(..., description="Campaign ID for tracking outreach emails")

class EmailResponse(BaseModel):
    """Email response model for outreach emails subject and body."""
    subject: str = Field(..., description="Subject of the outreach email")
    body: str = Field(..., description="Body of the outreach email")

class OutreachResp(BaseModel):
    emails: List[EmailResponse]

def send_email(receiver_email: str, subject: str, body: str):
    sender_email = "ankesh3905222@gmail.com"
    sender_password = "zqbe zgjg dcee vani"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print(f"Email sent to {receiver_email} with subject: {subject}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Initialize FastAPI app
app = FastAPI(
    title="Influencer Matching API",
    description="AI-powered influencer matching service using vector search",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only, be specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Response = {
    "influencers": [
        {
            "id": "425b8e5b734f528d18d69acb8118c29b",
            "username": "techwithtim",
            "email": "tim@123@gmail.com",
            "bio": "Programming tutorials, coding challenges, and tech career advice.",
            "followers": 1500000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/techwithtim/"
        },
        {
            "id": "fa8ae4383ffc31111e17c3974845eefd",
            "username": "jomatech",
            "email": "business@joma.io",
            "bio": "Tech and programming content.",
            "followers": 2280000,
            "platform": "YouTube",
            "link": "https://www.youtube.com/@jomakaze"
        },
        {
            "id": "cbe02b314c73c88faab11a4dd41eef3d",
            "username": "makeuplover.saba",
            "email": "saba.naveed29@yahoo.com",
            "bio": "Beauty Blogger | Makeup & Skincare Influencer",
            "followers": 25000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/makeuplover.saba/"
        },
        {
            "id": "3ff5e5474c4217615480ca2d2fb32695",
            "username": "makeupbyameliawebb",
            "email": "amelia.webb@example.com",
            "bio": "Freelance Makeup Artist | Melbourne",
            "followers": 65000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/makeupbyameliawebb/"
        },
        {
            "id": "c0fccecd95a0238d13f075de5c78df6b",
            "username": "mayamiay",
            "email": "maja@blazerinvestments.com",
            "bio": "Beauty Content Creator | Business Developer AFRICA/EU/USA/UAE/UK",
            "followers": 1000000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/mayamiay/"
        },
        {
            "id": "4b3e78d497024ff22c15c76d29e8d1b0",
            "username": "maryphillips",
            "email": "bookings@maneaddicts.com",
            "bio": "Celebrity Makeup Artist",
            "followers": 2300000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/maryphillips/"
        },
        {
            "id": "34d67325b6e2dad309629ab18a3adb67",
            "username": "garyvee",
            "email": "gary@vaynermedia.com",
            "bio": "CEO/Chairman @vaynermedia | Creator @veefriends | Investor in FB, Venmo, Twitter",
            "followers": 10400000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/garyvee/"
        },
        {
            "id": "5bb1a356d38031233da8ab75406c2130",
            "username": "makeuptutorialsx0x",
            "email": "makeuptutorialsx0x@outlook.com",
            "bio": "Beauty & Fashion | Product Reviews",
            "followers": 1000000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/makeuptutorialsx0x/"
        },
        {
            "id": "b1c73322eca15b326bff9d7463b99035",
            "username": "nikitabhardwaj00",
            "email": "nikita.bhardwaj@example.com",
            "bio": "Professional Makeup Artist | Based in Mumbai/Patna",
            "followers": 520800,
            "platform": "Instagram",
            "link": "https://www.instagram.com/nikitabhardwaj00/"
        },
        {
            "id": "2962da38350c33714c9fbacc80472032",
            "username": "missjasleenarora",
            "email": "jasleenarora996@gmail.com",
            "bio": "Beauty & Lifestyle Influencer",
            "followers": 3200000,
            "platform": "Instagram",
            "link": "https://www.instagram.com/missjasleenarora/"
        }
    ],
    "count": 10
}

def generate_deterministic_id(data):
    """Generate a deterministic ID based on username and email."""
    unique_str = data['username'] + data.get('email', '')
    return hashlib.md5(unique_str.encode()).hexdigest()

class AI_Matcher:
    def __init__(self):
        try:
            # Initialize Google Generative AI
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)
            # self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize the Pinecone client
            # self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI Matcher: {str(e)}")

    # def pineconeIndex_init(self):
    #     """Initialize Pinecone index connection."""
    #     index_name = "influencer-matching"

    #     try:
    #         pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    #         # Check if the index exists
    #         if not pc.has_index(index_name):
    #             raise HTTPException(status_code=404, detail=f"Index '{index_name}' does not exist.")

    #         # Connect to the existing index
    #         index = pc.Index(index_name)
    #         return index
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Failed to initialize Pinecone index: {str(e)}")

    # def push_influencer(self, influencer_data):
    #     """Push influencer data to Pinecone vector database."""
    #     try:
    #         index = self.pineconeIndex_init()
    #         docs = []

    #         for data in influencer_data:
    #             summary = f"bio: {data['bio']}, username: {data['username']}, followers: {data['followers']}, link: {data.get('link', '')}, platform: {data['platform']}"
    #             doc = Document(
    #                 page_content=summary,
    #                 metadata={
    #                     'username': data['username'],
    #                     'followers': data['followers'],
    #                     'email': data.get('email', ''),
    #                     'bio': data['bio'],
    #                     'link': data.get('link', ''),
    #                     'platform': data['platform']
    #                 }
    #             )
    #             docs.append(doc)

    #         vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
            
    #         # Generate deterministic IDs for each influencer
    #         ids = [generate_deterministic_id(data) for data in influencer_data]
    #         vectorstore.add_documents(documents=docs, ids=ids)
    #         return len(docs)
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Failed to push influencers: {str(e)}")
    
    # def query_influencer(self, query, k):
    #     """Query influencers from vector database based on similarity search."""
    #     try:
    #         index = self.pineconeIndex_init()
    #         vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
    #         results = vectorstore.similarity_search(query, k=k)
            
    #         influencers = []
    #         for result in results:
    #             influencer = {
    #                 'id': result.id if hasattr(result, 'id') else generate_deterministic_id({
    #                     'username': result.metadata['username'],
    #                     'email': result.metadata['email']
    #                 }),
    #                 'username': result.metadata['username'],
    #                 'followers': result.metadata['followers'],
    #                 'email': result.metadata.get('email', ''),
    #                 'bio': result.metadata['bio'],
    #                 'link': result.metadata.get('link', ''),
    #                 'platform': result.metadata.get('platform', 'Unknown')
    #             }
    #             influencers.append(influencer)
    #         return influencers
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Failed to query influencers: {str(e)}")

# Initialize AI Matcher instance
ai_matcher = AI_Matcher()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Influencer Matching API",
        "version": "1.0.0",
        "endpoints": {
            "push_influencers": "/influencers/push",
            "query_influencers": "/influencers/query",
            "search_influencers": "/influencers/search/{query}",
            "outreach_email": "/influencers/outreachEmailGenerator",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "AI Matcher is running"}

# @app.post("/influencers/push", response_model=dict)
# async def push_influencers(request: PushInfluencersRequest):
#     """Push influencer data to the vector database."""
#     try:
#         # Convert Pydantic models to dict
#         influencer_data = [influencer.dict() for influencer in request.influencers]
#         count = ai_matcher.push_influencer(influencer_data)
#         return {
#             "message": f"Successfully pushed {count} influencers",
#             "count": count
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/influencers/query", response_model=QueryResponse)
async def query_influencers(request: QueryRequest):
    """Query influencers based on search criteria."""
    try:
        # influencers = ai_matcher.query_influencer(request.query, request.k)
        return Response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/influencers/search/{query}")
async def search_influencers_get(query: str, k: int = 5):
    """Alternative GET endpoint for searching influencers (for simple queries)."""
    if k < 1 or k > 50:
        raise HTTPException(status_code=400, detail="k must be between 1 and 50")
    
    try:
        # influencers = ai_matcher.query_influencer(query, k)
        return Response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.post("/influencers/outreachEmailGenerator", response_model=OutreachResp)
async def generate_outreach_emails(request: OutreachData):
    try:
        influencers_list = request.influencers_data
        brand_name = request.brand_name
        brand_description = request.brand_description
        campaign_id = request.campaign_id

        if not isinstance(influencers_list, list):
            raise HTTPException(status_code=400, detail="Expected a list of influencer data.")

        emails = []

        for influencer in influencers_list:
            if not isinstance(influencer, dict):
                raise HTTPException(status_code=400, detail="Each influencer must be a dictionary.")
            
            receiver_email = influencer.get("email")
            if not receiver_email:
                continue  # skip if email missing

            # 🧠 LLM prompt & generation
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are an expert outreach email generator for the brand: {brand_name}. Brand Description: {brand_description}. Instructions: Generate short, eye-catching outreach emails under 200 words."),
                ("user", "Generate a personalized outreach email for the influencer: {influencer}. Don't include influencer name in the email")
            ])
            messages = prompt.format_messages(influencer=influencer)

            structured_resp = ai_matcher.llm.with_structured_output(EmailResponse)
            response: EmailResponse = structured_resp.invoke(messages)

            # 📧 Send the email
            send_email(receiver_email, response.subject, response.body + f"\nLets connect on http://localhost:5173/negotiation-chat/{campaign_id}")

            # 📥 Add to response list
            emails.append(response)

        return OutreachResp(emails=emails)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback to 8000 if PORT not set
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

    # ai_matcher = AI_Matcher()
    # ai_matcher.push_influencer(influencers)

    # Start command 
    # uvicorn app:app --host 0.0.0.0 --port 5050 --reload