import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/api/live-traffic")
async def get_live_traffic():
    # Import model locally to avoid circular import
    from api.index import svm_model
    
    if svm_model is None:
        raise HTTPException(status_code=500, detail="SVM model is not loaded on the server.")
        
    try:
        # Generate a small batch of random packets for polling (e.g., 3 to 8 packets)
        num_packets = np.random.randint(3, 8)
        features = np.random.rand(num_packets, 10)
        
        # Run prediction
        predictions = svm_model.predict(features)
        
        # Prepare results
        results = []
        current_time = datetime.now()
        
        for i, pred in enumerate(predictions):
            # Dummy model returns 0 or 1. Map 1 to Malicious, 0 to Normal.
            status = "Malicious" if pred == 1 else "Normal"
            action = "Blocked" if pred == 1 else "Allowed"
            
            # Generate mock network details for the response table
            src_ip = f"192.168.1.{np.random.randint(1, 255)}"
            dest_ip = f"10.0.0.{np.random.randint(1, 255)}"
            protocol = np.random.choice(["TCP", "UDP", "HTTP", "ICMP"])
            
            results.append({
                "timestamp": current_time.isoformat(),
                "source_ip": src_ip,
                "dest_ip": dest_ip,
                "protocol": protocol,
                "prediction": status,
                "action": action
            })
            

        # For the frontend response, we can add random IDs if needed, but the frontend might just use the timestamp
        for r in results:
            r["id"] = np.random.randint(10000, 99999)
            
        return JSONResponse(content={
            "status": "success",
            "count": len(results),
            "data": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating live traffic: {str(e)}")
