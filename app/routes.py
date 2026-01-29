from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from generation.generate_post import generate_vk_post

from etl.extract_vk import fetch_posts
from etl.clean_texts import clean_posts
from embeddings.build_index import build_faiss_index

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None}
    )

@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    topic: str = Form(...),
    tone: str = Form("тёплый"),
    length: str = Form("средний")
):
    result = generate_vk_post(
        topic=topic,
        tone=tone,
        length=length
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "topic": topic,
            "tone": tone,
            "length": length
        }
    )

@router.get("/collect", response_class=HTMLResponse)
def collect_page(request: Request):
    return templates.TemplateResponse(
        "collect.html",
        {"request": request}
    )


@router.post("/collect", response_class=HTMLResponse)
def collect_posts(
    request: Request,
    group_id: str = Form(...)
):
    try:
        # 1. Забираем посты
        fetch_posts(group_id, max_posts=2000)

        # 2. Чистим тексты
        clean_posts()

        # 3. Пересобираем embeddings
        build_faiss_index()

        message = f"Посты из группы «{group_id}» успешно добавлены и обработаны"

    except Exception as e:
        message = f"Ошибка при загрузке: {e}"

    return templates.TemplateResponse(
        "collect.html",
        {
            "request": request,
            "message": message
        }
    )