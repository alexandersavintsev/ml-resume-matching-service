from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pypdf import PdfReader
from docx import Document


router = APIRouter(tags=["webui"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/cabinet")
def cabinet_page(request: Request):
    return templates.TemplateResponse("cabinet.html", {"request": request})


@router.get("/predict-ui")
def predict_page(request: Request):
    return templates.TemplateResponse("predict.html", {"request": request})


@router.get("/history-ui")
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


@router.get("/logout")
def logout() -> RedirectResponse:
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("access_token", path="/")
    return resp


@router.post("/webui/extract-resumes")
async def extract_resumes(files: list[UploadFile] = File(...)) -> JSONResponse:
    extracted: list[str] = []
    invalid_files: list[str] = []

    for file in files:
        filename = file.filename or "unknown"
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        try:
            content = await file.read()

            if ext == "txt":
                text = content.decode("utf-8", errors="ignore").strip()

            elif ext == "pdf":
                reader = PdfReader(BytesIO(content))
                parts = []
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        parts.append(page_text)
                text = "\n".join(parts).strip()

            elif ext == "docx":
                doc = Document(BytesIO(content))
                text = "\n".join(p.text for p in doc.paragraphs).strip()

            else:
                invalid_files.append(filename)
                continue

            if text:
                extracted.append(text)
            else:
                invalid_files.append(filename)

        except Exception:
            invalid_files.append(filename)

    return JSONResponse(
        {
            "resumes": extracted,
            "invalid_files": invalid_files,
        }
    )
