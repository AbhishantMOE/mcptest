#!/usr/bin/env python3
"""
Test script to verify the MCP tool works with a public API
"""

import httpx
import asyncio

async def test_public_api():
    """Test with a publicly accessible API to verify the tool logic works"""
    try:
        async with httpx.AsyncClient() as client:
            # Test with httpbin.org public API
            response = await client.post("https://httpbin.org/post", 
                                       json={"db_name": "test_database"},
                                       timeout=10.0)
            response.raise_for_status()
            print("✅ HTTP client works with public APIs")
            print(f"Response status: {response.status_code}")
            return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

async def test_internal_api():
    """Test the actual internal API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://internalworks-v2.serv1.moeinternal.com/v2/iw/fetch-appid",
                                       json={"db_name": "test_database"},
                                       timeout=10.0)
            response.raise_for_status()
            print("✅ Internal API is accessible")
            return response.json()
    except Exception as e:
        print(f"❌ Internal API error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("Testing API connectivity...")
    print("\n1. Testing with public API:")
    result1 = asyncio.run(test_public_api())
    
    print("\n2. Testing with internal API:")
    result2 = asyncio.run(test_internal_api())
    
    print(f"\nPublic API result: {result1}")
    print(f"Internal API result: {result2}")