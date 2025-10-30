# backend/agents/orchestrator_agent.py
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from backend.core.llm_client import get_llm
from backend.core.logger import get_logger
from backend.config import Config

from langchain.agents import create_agent
from langchain_core.tools import tool

import requests

logger = get_logger("orchestrator_agent")
app = Flask(__name__)

# ---------------------------------------------------------
# 1️⃣ Pydantic Schemas
# ---------------------------------------------------------
class ParseRFPInput(BaseModel):
    file_text: str = Field(..., description="Raw RFP document text content to parse")

class GenerateResponseInput(BaseModel):
    question: str = Field(..., description="Specific question from RFP")
    context: str = Field("", description="Parsed or historical context")

class CreatePPTInput(BaseModel):
    summary: str = Field(..., description="Summary text used for PPT generation")


# ---------------------------------------------------------
# 2️⃣ Define Tools (each wrapped with @tool)
# ---------------------------------------------------------
AGENT_URLS = {
    "parser": "http://localhost:8001/parse",
    "response": "http://localhost:8002/generate_response",
    "ppt": "http://localhost:8003/create_ppt",
}

@tool("parse_rfp", args_schema=ParseRFPInput)
def parse_rfp_tool(file_text: str) -> str:
    """Parse the RFP document and extract questions and sections."""
    try:
        res = requests.post(AGENT_URLS["parser"], json={"file_text": file_text})
        res.raise_for_status()
        return res.json().get("result", "No result from parser agent.")
    except Exception as e:
        logger.exception("Error in parse_rfp_tool")
        return f"Error in parse_rfp_tool: {e}"

@tool("generate_response", args_schema=GenerateResponseInput)
def generate_response_tool(question: str, context: str = "") -> str:
    """Generate response text for a specific RFP question."""
    try:
        res = requests.post(AGENT_URLS["response"], json={"question": question, "context": context})
        res.raise_for_status()
        return res.json().get("answer", "No answer generated.")
    except Exception as e:
        logger.exception("Error in generate_response_tool")
        return f"Error in generate_response_tool: {e}"

@tool("create_ppt", args_schema=CreatePPTInput)
def create_ppt_tool(summary: str) -> str:
    """Generate a PowerPoint deck for the proposal."""
    try:
        res = requests.post(AGENT_URLS["ppt"], json={"summary": summary})
        res.raise_for_status()
        return res.json().get("ppt_path", "No PPT generated.")
    except Exception as e:
        logger.exception("Error in create_ppt_tool")
        return f"Error in create_ppt_tool: {e}"


# ---------------------------------------------------------
# 3️⃣ Initialize LLM and Agent (LangChain 1.0 LCEL)
# ---------------------------------------------------------
llm = get_llm(Config.LLM_PROVIDER)

tools = [parse_rfp_tool, generate_response_tool, create_ppt_tool]

# Modern ReAct agent creation
agent = create_agent(
    llm=llm,
    tools=tools,
    prompt=(
        "You are an orchestration assistant helping vendors reply to pharma RFPs. "
        "Decide which tool to use based on the user's instruction. "
        "If the query involves document parsing use `parse_rfp`, "
        "for question answering use `generate_response`, "
        "and for presentation creation use `create_ppt`."
    ),
)

# ---------------------------------------------------------
# 4️⃣ Flask endpoint
# ---------------------------------------------------------
@app.route("/process", methods=["POST"])
def process_rfp():
    data = request.json
    user_input = data.get("query") or data.get("instruction")
    logger.info(f"Received orchestration request: {user_input}")

    try:
        # New LCEL execution pattern
        result = agent.invoke({"input": user_input})
        output = result.get("output", str(result))
        return jsonify({"result": output})
    except Exception as e:
        logger.exception(f"Error during orchestration: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info("🚀 Starting Orchestrator Agent (LangChain 1.0+) on port 8000")
    app.run(host="0.0.0.0", port=8000)
