# backend/tools/orchestrator_tools.py
import requests
from langchain.tools import tool
from backend.core.logger import get_logger
from pydantic import BaseModel,Field
logger = get_logger(__name__)

# Tool Input Models
class ParseRFPInput(BaseModel):
    file_text: str = Field(..., description="Raw RFP document text content to parse")

class GenerateResponseInput(BaseModel):
    question: str = Field(..., description="Specific question from RFP")
    context: str = Field("", description="Parsed context or previous responses")

class CreatePPTInput(BaseModel):
    summary: str = Field(..., description="High-level summary for creating PPT")
AGENT_URLS = {
    "parser": "http://localhost:8001/parse",
    "response": "http://localhost:8002/generate_response",
    "ppt": "http://localhost:8003/create_ppt"
}

@tool("parse_rfp", args_schema=ParseRFPInput)
def parse_rfp_tool(file_text: str) -> str:
    """Parse the RFP document and extract sections, scope, and questions."""
    try:
        res = requests.post(AGENT_URLS["parser"], json={"file_text": file_text})
        return res.json().get("result", "No result from parser agent")
    except Exception as e:
        logger.exception("Error in parse_rfp_tool")
        return f"Error: {e}"

@tool("generate_response", args_schema=GenerateResponseInput)
def generate_response_tool(question: str, context: str = "") -> str:
    """Generate structured response for a specific RFP question."""
    try:
        res = requests.post(AGENT_URLS["response"], json={"question": question, "context": context})
        return res.json().get("answer", "No answer generated")
    except Exception as e:
        logger.exception("Error in generate_response_tool")
        return f"Error: {e}"

@tool("create_ppt", args_schema=CreatePPTInput)
def create_ppt_tool(summary: str) -> str:
    """Create a summary PowerPoint for the proposal."""
    try:
        res = requests.post(AGENT_URLS["ppt"], json={"summary": summary})
        return res.json().get("ppt_path", "No PPT generated")
    except Exception as e:
        logger.exception("Error in create_ppt_tool")
        return f"Error: {e}"
