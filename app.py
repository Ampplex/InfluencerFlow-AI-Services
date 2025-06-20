from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import uvicorn
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from pinecone import Pinecone
import os
import hashlib
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import json
from mock_data import temp_influencer, influencers
import smtplib
from email.message import EmailMessage
import random
import asyncio
import logging
import sys
from datetime import datetime
from contextlib import asynccontextmanager

# ============= LOGGING CONFIGURATION =============
# Configure logging before any other imports or code
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Ensure logs go to stdout
        logging.FileHandler('app.log', mode='a')  # Also log to file
    ]
)

# Create logger instance
logger = logging.getLogger(__name__)

# Set specific log levels for different components
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)

# Test logging immediately
logger.info("=" * 50)
logger.info("APPLICATION STARTUP - LOGGING INITIALIZED")
logger.info("=" * 50)

# Load environment variables from .env file
load_dotenv()

# Pydantic models for request/response
class InfluencerData(BaseModel):
    username: str
    email: str
    bio: str
    followers: int
    platform: str
    link: Optional[str] = None
    engagement_score: float = 0.0

class InfluencerResponse(BaseModel):
    id: str
    username: str
    email: str
    bio: str
    followers: int
    platform: str
    link: Optional[str] = None
    engagement_score: float

class QueryRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=50, description="Number of results to return (1-50)")

class FilteredInfluencersResponse(BaseModel):
    influencers: List[InfluencerResponse] = Field(..., description="List of influencers that precisely match the query.")

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
    campaign_description: str = Field(..., description="Campaign description to give the purpose of email in the body *Most Important*")

class EmailResponse(BaseModel):
    """Email response model for outreach emails subject and body."""
    subject: str = Field(..., description="Subject of the outreach email")
    body: str = Field(..., description="Body of the outreach email")

class OutreachResp(BaseModel):
    emails: List[EmailResponse]

def send_email(receiver_email: str, subject: str, body: str):
    """Send email using Brevo SMTP configuration."""
    logger.info(f"Attempting to send email to: {receiver_email}")
    
    # Get SMTP configuration from environment variables
    smtp_server = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME") 
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")
    
    # Validate required environment variables
    if not all([smtp_username, smtp_password, sender_email]):
        logger.error("❌ Missing required SMTP configuration in environment variables")
        raise HTTPException(
            status_code=500, 
            detail="SMTP configuration incomplete. Check environment variables."
        )

    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    try:
        # Use STARTTLS for port 587 (recommended) or SSL for port 465
        if smtp_port == 587:
            # STARTTLS connection (recommended for Brevo)
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()  # Enable encryption
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(msg)
        elif smtp_port == 465:
            # SSL connection
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(msg)
        else:
            # Plain SMTP (not recommended for production)
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(msg)
                
        logger.info(f"✅ Email sent successfully to {receiver_email} with subject: {subject}")
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed: {str(e)}")
        raise HTTPException(status_code=500, detail="SMTP Authentication failed. Check credentials.")
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {receiver_email}: {str(e)}")
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

def generate_deterministic_id(data):
    """Generate a deterministic ID based on username and email."""
    unique_str = data['username'] + data.get('email', '')
    return hashlib.md5(unique_str.encode()).hexdigest()

class AI_Matcher:
    def __init__(self):
        logger.info("🚀 Initializing AI_Matcher...")
        try:
            # Initialize Google Generative AI
            logger.info("Initializing Google Generative AI...")
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)
            logger.info("✅ Google Generative AI initialized successfully")
            
            logger.info("Initializing HuggingFace Embeddings...")
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("✅ HuggingFace Embeddings initialized successfully")
            
            # Initialize the Pinecone client
            logger.info("Initializing Pinecone client...")
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            logger.info("✅ Pinecone client initialized successfully")
            
            logger.info("🎉 AI_Matcher initialization completed successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Matcher: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI Matcher: {str(e)}")

    def pineconeIndex_init(self):
        """Initialize Pinecone index connection."""
        index_name = "influencer-matching"
        logger.info(f"Initializing Pinecone index: {index_name}")

        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            # Check if the index exists
            if not pc.has_index(index_name):
                logger.error(f"❌ Index '{index_name}' does not exist.")
                raise HTTPException(status_code=404, detail=f"Index '{index_name}' does not exist.")

            # Connect to the existing index
            index = pc.Index(index_name)
            logger.info(f"✅ Successfully connected to Pinecone index: {index_name}")
            return index
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone index: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize Pinecone index: {str(e)}")

    def push_influencer(self, influencer_data):
        """Push influencer data to Pinecone vector database."""
        logger.info(f"📤 Pushing {len(influencer_data)} influencers to Pinecone...")
        try:
            index = self.pineconeIndex_init()
            docs = []

            for i, data in enumerate(influencer_data):
                logger.debug(f"Processing influencer {i+1}/{len(influencer_data)}: {data.get('username', 'Unknown')}")
                summary = f"bio: {data['bio']}, username: {data['username']}, followers: {data['followers']}, link: {data.get('link', '')}, platform: {data['platform']}"
                doc = Document(
                    page_content=summary,
                    metadata={
                        'username': data['username'],
                        'followers': data['followers'],
                        'email': data.get('email', ''),
                        'bio': data['bio'],
                        'link': data.get('link', ''),
                        'platform': data['platform'],
                        'engagement_score': data.get('engagement_score', 0.0)
                    }
                )
                docs.append(doc)

            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
            
            # Generate deterministic IDs for each influencer
            ids = [generate_deterministic_id(data) for data in influencer_data]
            logger.info(f"Generated {len(ids)} unique IDs for influencers")
            
            vectorstore.add_documents(documents=docs, ids=ids)
            logger.info(f"✅ Successfully pushed {len(docs)} influencers to Pinecone")
            return len(docs)
        except Exception as e:
            logger.error(f"❌ Failed to push influencers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to push influencers: {str(e)}")
    
    def calculate_and_update_engagement_scores(self):
        """Calculates and updates engagement scores for all influencers in Pinecone."""
        logger.info("🔄 Starting engagement score calculation and update...")
        try:
            index = self.pineconeIndex_init()
            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")

            # Retrieve influencers
            logger.info("Fetching influencers for engagement score update...")
            all_influencer_docs = vectorstore.similarity_search("influencer", k=100)
            logger.info(f"Retrieved {len(all_influencer_docs)} influencers for score update")
            
            updates = []
            for i, doc in enumerate(all_influencer_docs):
                current_id = doc.id if hasattr(doc, 'id') else generate_deterministic_id(doc.metadata)
                current_followers = doc.metadata.get('followers', 0)
                
                # Calculate new engagement score
                new_engagement_score = round(float(current_followers) / 1000000 * (random.random() * 0.5 + 0.75), 2)
                new_engagement_score = max(0.0, min(10.0, new_engagement_score))
                
                logger.debug(f"Influencer {i+1}: {doc.metadata.get('username', 'Unknown')} - New score: {new_engagement_score}")
                
                # Create updated document
                updated_doc = Document(
                    page_content=doc.page_content,
                    metadata={
                        **doc.metadata,
                        'engagement_score': new_engagement_score
                    }
                )
                updates.append((updated_doc, current_id))

            if updates:
                updated_docs_only = [item[0] for item in updates]
                updated_ids_only = [item[1] for item in updates]
                vectorstore.add_documents(documents=updated_docs_only, ids=updated_ids_only)
                logger.info(f"✅ Updated engagement scores for {len(updates)} influencers")
            else:
                logger.warning("⚠️ No influencers found to update engagement scores")

        except Exception as e:
            logger.error(f"❌ Error calculating and updating engagement scores: {str(e)}")

    def assign_engagement_score_to_old_influencers(self):
        """Assigns an initial engagement_score of 0.0 to influencers that lack this field."""
        logger.info("🔧 Assigning engagement scores to old influencers...")
        try:
            index = self.pineconeIndex_init()
            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")

            logger.info("Checking for influencers without engagement_score...")
            candidate_docs = vectorstore.similarity_search("influencer", k=1000)
            logger.info(f"Checking {len(candidate_docs)} influencers for missing engagement scores")

            to_update = []
            for doc in candidate_docs:
                if 'engagement_score' not in doc.metadata:
                    influencer_id = doc.id if hasattr(doc, 'id') else generate_deterministic_id(doc.metadata)
                    
                    updated_metadata = {**doc.metadata, 'engagement_score': 0.0}
                    updated_doc = Document(
                        page_content=doc.page_content,
                        metadata=updated_metadata
                    )
                    to_update.append((updated_doc, influencer_id))
            
            if to_update:
                updated_docs_only = [item[0] for item in to_update]
                updated_ids_only = [item[1] for item in to_update]
                vectorstore.add_documents(documents=updated_docs_only, ids=updated_ids_only)
                logger.info(f"✅ Successfully assigned engagement_score to {len(to_update)} old influencers")
            else:
                logger.info("ℹ️ No old influencers found missing engagement_score")

        except Exception as e:
            logger.error(f"❌ Error assigning engagement_score to old influencers: {str(e)}")

    def get_influencers(self, query=" ", k=100):
        index = self.pineconeIndex_init()
        vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
        retrieved_docs = vectorstore.similarity_search(query, k=k)
        
        return retrieved_docs

    def query_influencer(self, query, k):
        """Query influencers from vector database based on similarity search, then refine using LLM."""
        logger.info(f"🔍 Querying influencers with query: '{query}', k={k}")
        try:
            index = self.pineconeIndex_init()
            vectorstore = PineconeVectorStore(index=index, embedding=self.embeddings, namespace="Influencers")
            
            # Step 1: Retrieve initial candidates from Pinecone
            logger.info("Performing similarity search...")
            retrieved_docs = vectorstore.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(retrieved_docs)} candidates from Pinecone")
            
            if not retrieved_docs:
                logger.warning("⚠️ No influencers found in similarity search")
                return []

            # Step 1.5: Rank retrieved documents by engagement_score (descending) before LLM
            retrieved_docs.sort(key=lambda doc: doc.metadata.get('engagement_score', 0.0), reverse=True)
            logger.info(f"Candidates re-ranked by engagement_score. Top score: {retrieved_docs[0].metadata.get('engagement_score', 'N/A')}")

            # Step 2: Prepare context for the LLM
            logger.info("Preparing context for LLM refinement...")
            context_str = ""
            for i, doc in enumerate(retrieved_docs):
                influencer_id = doc.id if hasattr(doc, 'id') else generate_deterministic_id(doc.metadata)
                context_str += (
                    f"Influencer {i+1}:\n"
                    f"  ID: {influencer_id}\n"
                    f"  Username: {doc.metadata.get('username', 'N/A')}\n"
                    f"  Bio: {doc.metadata.get('bio', 'N/A')}\n"
                    f"  Followers: {doc.metadata.get('followers', 'N/A')}\n"
                    f"  Platform: {doc.metadata.get('platform', 'N/A')}\n"
                    f"  Email: {doc.metadata.get('email', 'N/A')}\n"
                    f"  Link: {doc.metadata.get('link', 'N/A')}\n"
                    f"  Engagement Score: {doc.metadata.get('engagement_score', 0.0)}\n"
                    f"---\n"
                )

            # Step 3: Create LLM prompt for re-ranking/filtering
            logger.info("Invoking LLM for result refinement...")
            system_template = (
                "You are an expert influencer matcher. Your task is to review a list of influencers provided below "
                "and identify only those who *precisely* match the user's query. "
                "Output the matching influencers in a JSON array format, strictly following the provided schema. "
                "If no influencers precisely match, return an empty list."
                "Do not include any conversational text or explanations, only the JSON."
            )
            human_template = (
                "Here is the user's query: {query}\n\n"
                "Here are the candidate influencers:\n{context}"
            )

            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_template),
                HumanMessagePromptTemplate.from_template(human_template)
            ])

            # Step 4: Invoke the LLM with structured output
            llm_chain = prompt | self.llm.with_structured_output(FilteredInfluencersResponse)
            llm_response = llm_chain.invoke({"query": query, "context": context_str})
            
            logger.info(f"✅ LLM returned {len(llm_response.influencers)} refined matches")
            return llm_response.influencers
        except Exception as e:
            logger.error(f"❌ Failed to query and refine influencers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to query and refine influencers: {str(e)}")

# Initialize AI Matcher instance
logger.info("Creating AI_Matcher instance...")
ai_matcher = AI_Matcher()

# ============= FASTAPI ENDPOINTS =============

@app.get("/")
async def root():
    """Root endpoint with API information."""
    logger.info("📍 Root endpoint accessed")
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
    logger.info("💓 Health check endpoint accessed")
    return {"status": "healthy", "message": "AI Matcher is running"}

@app.post("/influencers/push", response_model=dict)
async def push_influencers(request: PushInfluencersRequest):
    """Push influencer data to the vector database."""
    logger.info(f"📥 Push influencers endpoint called with {len(request.influencers)} influencers")
    try:
        # Convert Pydantic models to dict
        influencer_data = [influencer.dict() for influencer in request.influencers]
        count = ai_matcher.push_influencer(influencer_data)
        logger.info(f"✅ Successfully processed push request for {count} influencers")
        return {
            "message": f"Successfully pushed {count} influencers",
            "count": count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in push_influencers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/influencers/query", response_model=QueryResponse)
async def query_influencers(request: QueryRequest):
    """Query influencers based on search criteria."""
    logger.info(f"🔍 Query influencers endpoint called with query: '{request.query}', k={request.k}")
    try:
        influencers = ai_matcher.query_influencer(request.query, request.k)
        logger.info(f"✅ Query completed, returning {len(influencers)} influencers")
        return QueryResponse(
            influencers=influencers,
            count=len(influencers)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in query_influencers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/influencers/search/{query}")
async def search_influencers_get(query: str, k: int = 5):
    """Alternative GET endpoint for searching influencers (for simple queries)."""
    logger.info(f"🔍 GET search endpoint called with query: '{query}', k={k}")
    if k < 1 or k > 50:
        logger.warning(f"⚠️ Invalid k value: {k} (must be between 1 and 50)")
        raise HTTPException(status_code=400, detail="k must be between 1 and 50")
    
    try:
        influencers = ai_matcher.query_influencer(query, k)
        logger.info(f"✅ GET search completed, returning {len(influencers)} influencers")
        return QueryResponse(
            influencers=influencers,
            count=len(influencers)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in search_influencers_get: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.post("/influencers/outreachEmailGenerator", response_model=OutreachResp)
async def generate_outreach_emails(request: OutreachData):
    logger.info(f"📧 Outreach email generation started for {len(request.influencers_data)} influencers")
    logger.info(f"Brand: {request.brand_name}, Campaign: {request.campaign_id}")
    
    try:
        influencers_list = request.influencers_data
        brand_name = request.brand_name
        brand_description = request.brand_description
        campaign_id = request.campaign_id
        campaign_description = request.campaign_description

        if not isinstance(influencers_list, list):
            logger.error("❌ Invalid influencers_data format - expected list")
            raise HTTPException(status_code=400, detail="Expected a list of influencer data.")

        emails = []
        successful_sends = 0
        failed_sends = 0

        for i, influencer in enumerate(influencers_list):
            logger.info(f"Processing influencer {i+1}/{len(influencers_list)}: {influencer.get('username', 'Unknown')}")
            
            if not isinstance(influencer, dict):
                logger.error(f"❌ Invalid influencer format at index {i}")
                raise HTTPException(status_code=400, detail="Each influencer must be a dictionary.")
            
            receiver_email = influencer.get("email")
            if not receiver_email:
                logger.warning(f"⚠️ Skipping influencer {i+1} - no email provided")
                continue

            try:
                # LLM prompt & generation
                logger.debug(f"Generating email for {receiver_email}")
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"You are an expert outreach email generator for the brand: {brand_name}. The body should include and highlight the campaign description {campaign_description} also give a short intro of brand - Brand Description: {brand_description} in the starting the explain about campaign. Instructions: Generate short, eye-catching outreach emails under 200 words."),
                    ("user", "Generate a personalized outreach email for the influencer: {influencer}, keep the subject and body separate in json")
                ])
                messages = prompt.format_messages(influencer=influencer)

                structured_resp = ai_matcher.llm.with_structured_output(EmailResponse)
                response: EmailResponse = structured_resp.invoke(messages)

                # Send the email
                send_email(receiver_email, response.subject, response.body + f"\nLets connect on https://app.influencer.in/negotiation-chat/{campaign_id}/{receiver_email}")
                
                emails.append(response)
                successful_sends += 1
                logger.info(f"✅ Successfully processed influencer {i+1}")
                
            except Exception as email_error:
                failed_sends += 1
                logger.error(f"❌ Failed to process influencer {i+1}: {str(email_error)}")
                continue

        logger.info(f"📊 Outreach completed - Success: {successful_sends}, Failed: {failed_sends}")
        return OutreachResp(emails=emails)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in generate_outreach_emails: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ============= STARTUP EVENTS =============

# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("🚀 FastAPI application startup event triggered")
    logger.info("Starting background engagement score scheduler...")

    # Background task for periodic engagement score updates
    async def start_update_scheduler():
        while True:
            try:
                logger.info("🔄 Running scheduled engagement score update...")
                ai_matcher.calculate_and_update_engagement_scores()  # Ensure ai_matcher is defined
                logger.info("✅ Scheduled engagement score update completed")
            except Exception as e:
                logger.error(f"❌ Error in scheduled engagement score update: {str(e)}")
            await asyncio.sleep(21600)  # Update every 6 hours

    # Start the background task
    task = asyncio.create_task(start_update_scheduler())
    logger.info("✅ Background scheduler started successfully")

    try:
        yield  # Hand control back to FastAPI to run the application
    finally:
        # Shutdown logic
        logger.info("🛑 FastAPI application shutdown event triggered")
        task.cancel()  # Cancel the background task on shutdown
        try:
            await task  # Ensure the task is properly cancelled
        except asyncio.CancelledError:
            logger.info("✅ Background scheduler stopped successfully")

# Assign lifespan to FastAPI app
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    logger.info("🎯 Starting application from main...")
    
    # Manual call for one-time data migration (commented out):
    # ai_matcher.assign_engagement_score_to_old_influencers()

    # logger.info("🚀 Starting uvicorn server on port 8080...")
    # uvicorn.run(
    #     "app:app",
    #     host="0.0.0.0",
    #     port=int(os.getenv("PORT", 8080)),
    #     log_level="info"
    # )
    resp = AI_Matcher().get_influencers()
    print(resp)

    # Start command: uvicorn app:app --host 0.0.0.0 --port 5050 --reload --log-level info