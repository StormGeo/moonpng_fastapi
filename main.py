from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from utils.logger import get_logger
from app.api.v1.moonpng import router as moonpng_router

logger = get_logger()


app = FastAPI(debug=True, title="MoonPNG API", description="API para geração de imagens meteorológicas em formato PNG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou liste domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Starting MoonPNG API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    log_data = {
        "endpoint": request.url.path,
        "method": request.method,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }

    try:
        response = await call_next(request)
        log_data["status_code"] = response.status_code
    except Exception as e:
        log_data["status_code"] = 500
        log_data["error"] = str(e)
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        log_data["duration_ms"] = round(duration, 2)
        logger.info(log_data)

    return response


app.include_router(moonpng_router)

