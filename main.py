
import uvicorn
import os 
# from core.config import config

if __name__ == "__main__":
    uvicorn.run(
        app="core.server:app",
        reload=True if os.getenv("ENVIRONMENT") != "production" else False,
        workers=1,
        host="0.0.0.0", port=5010
    )
