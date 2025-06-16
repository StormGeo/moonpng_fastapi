# fastapi_moonpng

This project exposes a small FastAPI service for generating meteorological PNG images. The application can be started locally with:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API provides two endpoints under `/moonpng` to retrieve images via `GET` or `POST` requests.
