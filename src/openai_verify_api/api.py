from __future__ import annotations

from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from openai_verify_api.models import VerificationResponse
from openai_verify_api.services.verifier import OpenAIVerifyError, verifier, verify_image


app = FastAPI(title="OpenAI Verify API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/verify", response_model=VerificationResponse)
def verify(file: UploadFile = File(...)) -> VerificationResponse:
    suffix = Path(file.filename or "upload.bin").suffix
    with NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        try:
            file.file.seek(0)
            copyfileobj(file.file, temp_file)
        finally:
            file.file.close()

    try:
        return verify_image(temp_path, media_type=file.content_type)
    except OpenAIVerifyError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        return JSONResponse(status_code=500, content={"filename": file.filename, "detail": f"Verification failed: {error}"})
    finally:
        temp_path.unlink(missing_ok=True)


@app.on_event("shutdown")
def shutdown() -> None:
    verifier.close()
