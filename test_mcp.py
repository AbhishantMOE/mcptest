import os
import httpx
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
import uvicorn
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---

# The variable that Render's start command `uvicorn test_mcp:app` will look for.
# The FastMCP class is a type of FastAPI application, so we create it as `app`.
app = FastMCP(
    title="MoEngage Internal Works API",
    description="This server provides secure access to MoEngage Internal Works API for fetching application IDs. Supports Bearer token authentication and follows MCP specification for seamless Intercom integration. Use this connector to retrieve application IDs from MoEngage's internal works system by providing database name and region parameters.",
    version="1.0.0",
)

# The base URL for the external API you are calling
API_BASE_URL = "https://intercom-api-gateway.moengage.com/v2/iw"

# Get the bearer token from an environment variable for security
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    # This will stop the app from starting if the token is missing
    raise ValueError("FATAL ERROR: The BEARER_TOKEN environment variable is not set.")


# --- DATA MODELS ---

class FetchAppidRequest(BaseModel):
    db_name: str = Field(
        ...,
        description="The name of the database to fetch the application ID for."
    )
    region: str = Field(
        ...,
        description="The region for the database (e.g., DC1)."
    )


# --- API TOOL DEFINITION ---

# The @app.tool() decorator adds this function as an API endpoint to our application
@app.tool()
async def fetch_appid(request: FetchAppidRequest) -> Dict[str, Any]:
    """
    Fetches the application ID for a given database name and region.
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {BEARER_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = request.dict() # Use the model's dict() method
            
            response = await client.post(
                f"{API_BASE_URL}/fetch-appid",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Successfully fetched app ID for db_name: {request.db_name}")
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
        return {"error": f"Downstream API error: {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error: {e}")
        return {"error": "Could not connect to the downstream API."}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected server error occurred."}


# --- LOCAL DEVELOPMENT ---

# This block is for running the server on your local machine
# It is not used by Render's start command.
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="http", host="0.0.0.0", port=port)
