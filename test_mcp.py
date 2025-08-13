import os
import httpx
from typing import Dict, Any
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from fastapi import FastAPI

# Define the model for the API request body to ensure data validation
class FetchAppidRequest(BaseModel):
    db_name: str = Field(
        ...,
        description="The name of the database to fetch the application ID for."
    )
    region: str = Field(
        ...,
        description="The region for the database (e.g., DC1)."
    )

# Create an instance of FastMCP
mcp = FastMCP()

# Create a FastAPI app
app = FastAPI(
    title="MoEngage Internal Works API",
    description="This server provides secure access to MoEngage Internal Works API for fetching application IDs. Supports Bearer token authentication and follows MCP specification for seamless Intercom integration.",
    version="1.0.0",
)

# Mount the MCP server to the FastAPI app
app = mcp.mount_to_app(app, path="/mcp")

@mcp.tool()
async def fetch_appid(request: FetchAppidRequest) -> Dict[str, Any]:
    """
    Fetches the application ID for a given database name from the internal works API.

    Args:
        request: The request body containing the database name and region.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Make a POST request to the internal works API
            api_url = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
            
            # Get bearer token from environment variable or use a default one
            auth_token = os.environ.get("AUTH_HEADER", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg")
            
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                api_url,
                json={"db_name": request.db_name, "region": request.region},
                headers=headers,
                timeout=10.0
            )
            
            # Raise an exception for HTTP errors
            response.raise_for_status()
            
            # Log the successful API call
            print(f"Successfully fetched app ID for db_name: {request.db_name}, region: {request.region}")
            
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

# This block ensures the server runs when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
