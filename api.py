from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.portfolio_assistant.crew import PortfolioAssistant
import uvicorn
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
import agentops

load_dotenv()

agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Check if API key is loaded correctly
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Missing OPENAI_API_KEY in environment variables")

# Initialize FastAPI
app = FastAPI(title="Portfolio Assistant Chatbot API", version="1.0")

# Initialize the Portfolio Assistant
portfolio_assistant = PortfolioAssistant()

class UserQuery(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.post("/ask")
async def ask_question(query: UserQuery):
    """
    Endpoint to process user questions and get responses from the CrewAI system.
    """
    try:
        logger.info(f"Processing question: {query.question}")
        # Create crew with the specific question
        crew = portfolio_assistant.crew(question=query.question)
        inputs = {"question": query.question}
        response = crew.kickoff(inputs=inputs)
        return {"answer": response}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
