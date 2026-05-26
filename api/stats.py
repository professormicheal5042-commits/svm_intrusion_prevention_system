from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.db import supabase

router = APIRouter()

@router.get("/api/stats")
async def get_stats(user_id: str = None):
    try:
        if not user_id:
            # If no user_id is provided, return empty stats for security
            return JSONResponse(content={
                "status": "success",
                "metrics": {"total": 0, "malicious": 0, "normal": 0, "accuracy": 0},
                "charts": {
                    "pie_chart": {"labels": ["Normal", "Malicious"], "data": [0, 0]},
                    "bar_chart": {"labels": ["DDoS", "Port Scan", "Malware", "Normal"], "data": [0, 0, 0, 0]}
                }
            })

        # Fetch logs from Supabase
        query = supabase.table("traffic_logs").select("*").eq("user_id", user_id)
        response = query.limit(100000).execute()
        logs = response.data
        
        total_packets = len(logs)
        
        # Aggregate Normal vs Malicious for Pie Chart
        malicious_count = sum(1 for log in logs if log.get('prediction') == 'Malicious')
        normal_count = total_packets - malicious_count
        
        # Aggregate by Protocol (Mocking "Attack Types" for Bar Chart)
        # Assuming different protocols represent different potential attack vectors in our mock data
        protocols = {}
        for log in logs:
            proto = log.get('protocol', 'Unknown')
            if log.get('prediction') == 'Malicious':
                protocols[proto] = protocols.get(proto, 0) + 1
                
        bar_chart_labels = list(protocols.keys())
        bar_chart_data = list(protocols.values())
        

        # Model Performance Metrics (Static / Mocked for the dummy model)
        # In a real app, this would come from the model evaluation phase
        accuracy = 96.7
        precision = 94.2
        recall = 95.1
        f1_score = 94.6
        
        # Confusion Matrix (Mocked based on typical SVM performance)
        # [ [True Negative, False Positive], [False Negative, True Positive] ]
        confusion_matrix = [
            [normal_count - int(normal_count * 0.05), int(normal_count * 0.05)],
            [int(malicious_count * 0.1), malicious_count - int(malicious_count * 0.1)]
        ]

        return JSONResponse(content={
            "status": "success",
            "metrics": {
                "total": total_packets,
                "malicious": malicious_count,
                "normal": normal_count,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            },
            "charts": {
                "pie_chart": {
                    "labels": ["Normal", "Malicious"],
                    "data": [normal_count, malicious_count]
                },
                "bar_chart": {
                    "labels": bar_chart_labels,
                    "data": bar_chart_data
                },
                "confusion_matrix": confusion_matrix
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
