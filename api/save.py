from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Any, Optional

router = APIRouter()

BATCH_SIZE = 100   # Supabase free-tier safe batch insert limit


class SaveRequest(BaseModel):
    results: List[Any]
    filename: str = "unknown"
    user_id: Optional[str] = None   # Optional so null from JS is accepted


@router.post("/api/save")
async def save_results(payload: SaveRequest):
    """
    Save upload analysis results to Supabase traffic_logs.

    Steps:
      1. Require user_id — refuse anonymous saves to prevent cross-user pollution.
      2. DELETE all existing rows owned by this user (wipe-before-write).
      3. INSERT the new rows in batches of BATCH_SIZE to stay within
         Supabase free-tier limits and prevent duplicates.
    """
    if not payload.user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id is required. Please log in before saving."
        )

    try:
        from api.db import supabase

        # ── Build insert payload ──────────────────────────────────────────────
        to_insert = []
        for r in payload.results:
            to_insert.append({
                "source_ip":  r.get("source_ip",  "0.0.0.0"),
                "dest_ip":    r.get("dest_ip",    "0.0.0.0"),
                "protocol":   r.get("protocol",   "TCP"),
                "prediction": r.get("prediction", "Normal"),
                "action":     r.get("action",     "Allowed"),
                "timestamp":  r.get("timestamp",  None),
                "user_id":    payload.user_id,
            })

        if not to_insert:
            return JSONResponse(content={
                "status": "success",
                "saved": 0,
                "filename": payload.filename,
                "message": "No records to save."
            })

        # ── Step 1: Wipe existing records for this user ───────────────────────
        del_resp = supabase.table("traffic_logs") \
            .delete() \
            .eq("user_id", payload.user_id) \
            .execute()

        # ── Step 2: Insert in safe batches ────────────────────────────────────
        saved = 0
        for start in range(0, len(to_insert), BATCH_SIZE):
            chunk = to_insert[start: start + BATCH_SIZE]
            supabase.table("traffic_logs").insert(chunk).execute()
            saved += len(chunk)

        return JSONResponse(content={
            "status": "success",
            "saved": saved,
            "filename": payload.filename,
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save results: {str(e)}"
        )
