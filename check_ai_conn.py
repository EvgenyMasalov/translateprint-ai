import httpx
import asyncio

async def check_connection():
    urls = [
        "https://api.anthropic.com",
        "https://api.openai.com",
        "https://google.com"
    ]
    
    print("--- AI Connectivity Check ---")
    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                response = await client.get(url, timeout=5.0)
                print(f"[OK] {url} - Status: {response.status_code}")
            except Exception as e:
                print(f"[FAIL] {url} - Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_connection())
