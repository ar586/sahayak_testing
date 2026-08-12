from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from chat_service import generate_chat_response, generate_streaming_chat_response
from database import get_chat_history, get_all_notices, get_notice_by_id, save_fcm_token, get_fcm_tokens, remove_fcm_token
from run import scrape_notices
import os
from notification_service import init_firebase, send_multicast_message


app = FastAPI(title="Notice Chat API", version="2.0.0")

# Initialize Firebase Admin
init_firebase()

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    query: str
    user_id: str
    notice_id: str
    user_branch: str
    user_year: str

class ChatResponse(BaseModel):
    response: str
    notice_id: str

class HistoryResponse(BaseModel):
    user_id: str
    notice_id: str
    messages: list

class TokenRequest(BaseModel):
    user_id: str
    token: str

class SendNotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str

@app.get("/firebase-messaging-sw.js")
async def get_sw():
    return FileResponse(os.path.join(static_path, "firebase-messaging-sw.js"), media_type="application/javascript")

@app.post("/api/fcm/token")
async def register_token(request: TokenRequest):
    """
    Register or update FCM token for a user.
    """
    try:
        if not request.user_id or not request.token:
            raise HTTPException(status_code=400, detail="Missing user_id or token")
        
        save_fcm_token(request.user_id, request.token)
        return {"status": "success", "message": "Token registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/fcm/token")
async def unregister_token(request: TokenRequest):
    """
    Unregister an FCM token for a user.
    """
    try:
        if not request.user_id or not request.token:
            raise HTTPException(status_code=400, detail="Missing user_id or token")
        
        remove_fcm_token(request.user_id, request.token)
        return {"status": "success", "message": "Token unregistered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fcm/send")
async def send_notification(request: SendNotificationRequest):
    """
    Send a push notification to a specific user.
    """
    try:
        tokens = get_fcm_tokens(request.user_id)
        if not tokens:
            return {"status": "skipped", "message": "No tokens found for user"}
        
        # Send using service
        result = send_multicast_message(request.title, request.body, tokens)
        
        return {
            "status": "success",
            "success_count": result["success_count"],
            "failure_count": result["failure_count"]
        }
    except Exception as e:
        print(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class NoticeListItem(BaseModel):
    id: str = Field(alias="_id")
    title: str
    date: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[dict] = None
    
    class Config:
        populate_by_name = True

class NoticeDetail(BaseModel):
    id: str = Field(alias="_id")
    title: str
    date: Optional[str] = None
    summary: Optional[str] = None
    extracted_text: Optional[str] = None
    tags: Optional[dict] = None
    link: Optional[str] = None
    cached_url: Optional[str] = None
    
    class Config:
        populate_by_name = True

# Helper to find absolute path to static
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_path):
    # Fallback if running from root
    static_path = "static"

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Notice Chat API v2.0 is running"}

@app.get("/api/cron/update-notices")
async def trigger_update_notices(background_tasks: BackgroundTasks):
    """
    Trigger the notice scraper in the background.
    Ideal for cron jobs.
    """
    try:
        background_tasks.add_task(scrape_notices)
        return {"status": "accepted", "message": "Notice update started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notices")
async def list_notices(page: int = 1, limit: int = 20):
    """
    Get all notices for frontend display with pagination.
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 20)
    
    Returns:
        List of notices with basic info
    """
    try:
        notices = get_all_notices(page, limit)
        return notices
    except Exception as e:
        print(f"Error listing notices: {e}")
        return []
        # raise HTTPException(status_code=500, detail=str(e))

@app.get("/notices/search")
async def search_notices_endpoint(q: str, page: int = 1, limit: int = 20):
    """
    Search notices by query string.
    """
    from database import search_notices
    try:
        if not q.strip():
            return []
            
        notices = search_notices(q, page, limit)
        return notices
    except Exception as e:
        print(f"Error searching notices endpoint: {e}")
        return []

@app.get("/notices/{notice_id}")
async def get_notice(notice_id: str):
    """
    Get full details of a specific notice.
    
    Args:
        notice_id: Notice ID
    
    Returns:
        Complete notice details
    """
    try:
        notice = get_notice_by_id(notice_id)
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")
        return notice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat about a specific notice.
    
    Args:
        request: ChatRequest with query, user_id, notice_id, user_branch, user_year
    
    Returns:
        ChatResponse with LLM response
    """
    try:
        # Validate inputs
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if not request.user_id or not request.notice_id:
            raise HTTPException(
                status_code=400, 
                detail="user_id and notice_id are required"
            )
        
        if not request.user_branch or not request.user_year:
            raise HTTPException(
                status_code=400, 
                detail="user_branch and user_year are required"
            )
        
        # Stream response
        return StreamingResponse(
            generate_streaming_chat_response(
                query=request.query,
                user_id=request.user_id,
                notice_id=request.notice_id,
                user_branch=request.user_branch,
                user_year=request.user_year
            ),
            media_type="text/event-stream",
            headers={
                "X-Stream": "true",
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{user_id}/{notice_id}", response_model=HistoryResponse)
async def get_history(user_id: str, notice_id: str, limit: int = 10):
    """
    Retrieve chat history for a specific user and notice.
    
    Args:
        user_id: User ID
        notice_id: Notice ID
        limit: Maximum number of messages to retrieve
    
    Returns:
        HistoryResponse with messages
    """
    try:
        messages = get_chat_history(user_id, notice_id, limit=limit)
        return HistoryResponse(
            user_id=user_id,
            notice_id=notice_id,
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
