from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


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


@router.get("/predict")
def predict_page(request: Request):
    return templates.TemplateResponse("predict.html", {"request": request})


@router.get("/history")
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


@router.get("/logout")
def logout() -> RedirectResponse:
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("access_token", path="/")
    return resp
