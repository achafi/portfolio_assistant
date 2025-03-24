from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.portfolio_assistant.crew import PortfolioAssistant
import uvicorn
import os

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Check if API key is loaded correctly
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("❌ Missing OPENAI_API_KEY in environment variables")

app = FastAPI(title="Portfolio Assistant Chatbot API", version="1.0")


# Initialize the Crew
crew = PortfolioAssistant().crew()


class UserQuery(BaseModel):
    question: str


# Initialize FastAPI
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.post("/ask")
async def ask_question(query: UserQuery):
    """
    Endpoint to process user questions and get responses from the CrewAI system.
    """
    try:
        inputs = {"question": query.question}
        response = crew.kickoff(inputs=inputs)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
