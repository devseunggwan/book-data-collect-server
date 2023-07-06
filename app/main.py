from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import mongo
from app.models import BookModel
from app.scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "./index.html", {"request": request, "title": "콜렉터 북북이"}
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    # 1, 쿼리에서 검색어 추출
    keyword = request.query_params.get("q")
    context = None

    # (예외처리)
    # - 검색어가 없다면 사용자에게 검색을 요구 return
    if not keyword:
        context = {"request": request}
    # - 기존에 검색된 데이터가 있으면 저장된 데이터를 가져옵니다.
    elif await mongo.engine.find_one(BookModel, BookModel.keyword == keyword):
        books = await mongo.engine.find(BookModel, BookModel.keyword == keyword)
        context = {"request": request, "keyword": keyword, "books": books}
    # - 기존에 검색된 데이터가 없다면
    else:
        # 2. 데이터 수집기로 해당 검색어에 대해 데이터를 수집합니다.
        naver_book_scraper = NaverBookScraper()
        books = await naver_book_scraper.search(keyword, 10)
        book_models = [
            BookModel(
                keyword=keyword,
                publisher=book["publisher"],
                discount=book["discount"],
                image=book["image"],
            )
            for book in books
        ]

        # 3. DB에 수집된 데이터를 저장합니다.
        await mongo.engine.save_all(book_models)
        context = {"request": request, "keyword": keyword, "books": books}

    return templates.TemplateResponse("./index.html", context=context)


@app.on_event("startup")
async def on_app_start():
    mongo.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    mongo.close()
