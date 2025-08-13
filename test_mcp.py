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

# Define the model for the API request body
class FetchAppidRequest(BaseModel):
    db_name: str = Field(
        ...,
        description="The name of the database to fetch the application ID for."
    )
    region: str = Field(
        ...,
        description="The region for the database (e.g., DC1)."
    )

# The base URL for the external API
API_BASE_URL = "https://intercom-api-gateway.moengage.com/v2/iw"

# Get the bearer token from an environment variable for security
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN environment variable not set.")

# Initialize FastMCP AS the application itself.
# The `uvicorn` command looks for a variable named `app`.
app = FastMCP(
    name="MoEngage Internal Works API",
    instructions="This server provides secure access to MoEngage Internal Works API for fetching application IDs. Supports Bearer token authentication and follows MCP specification for seamless Intercom integration. Use this connector to retrieve application IDs from MoEngage's internal works system by providing database name and region parameters."
)

# Use the app instance to decorate the tool
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
            payload = {
                "db_name": request.db_name,
                "region": request.region
            }
            response = await client.post(
                f"{API_BASE_URL}/fetch-appid",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Successfully fetched app ID for db_name: {request.db_name}, region: {request.region}")
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP Error occurred: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

# This block is for local development and is not used by Render's start command
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Note: Pass the app object directly for local runs
    uvicorn.run(app, host="0.0.0.0", port=port)
