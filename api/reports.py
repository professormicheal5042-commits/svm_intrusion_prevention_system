from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.db import supabase

router = APIRouter()

@router.get("/api/reports")
async def get_reports(user_id: str = None):
    try:
        if not user_id:
            return JSONResponse(content={"status": "success", "data": []})

        from api.db import supabase
        query = supabase.table("traffic_logs").select("*").order("timestamp", desc=True).eq("user_id", user_id)
        response = query.limit(100000).execute()
        
        return JSONResponse(content={
            "status": "success",
            "data": response.data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")
