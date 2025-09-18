
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import json
import asyncio

from pydantic import BaseModel
from query_engine import get_bot_response_stream

app = FastAPI()

# Mount static files directory
app.mount("/backend/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.get("/widget")
async def get_widget():
    return FileResponse("static/widget.html")

@app.post("/chat")
async def chat(request: QueryRequest):
    async def stream_response():
        try:
            # Add CORS headers for SSE
            yield "data: " + json.dumps({"type": "start"}) + "\n\n"
            
            for token in get_bot_response_stream(request.query):
                # Send each token as JSON to handle special characters properly
                data = json.dumps({"type": "token", "content": token})
                yield f"data: {data}\n\n"
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            # Send end signal
            yield "data: " + json.dumps({"type": "end"}) + "\n\n"
            
        except Exception as e:
            # Send error message
            error_data = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        stream_response(), 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Keep the non-streaming endpoint as fallback
@app.post("/chat-sync", response_model=QueryResponse)
async def chat_sync(request: QueryRequest):
    from query_engine import get_bot_response
    response = get_bot_response(request.query)
    return QueryResponse(response=response)

@app.get("/")
async def root():
    return {"message": "AssortTech Chatbot backend is running."}