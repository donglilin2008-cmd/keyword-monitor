from fastapi import FastAPI, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pathlib, sys
BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))
import database, crawler

app = FastAPI(title="关键词实况监控 - Prolockey")
templates = Jinja2Templates(directory=str(BASE / "templates"))
database.init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/platforms")
async def api_platforms():
    return database.get_platforms()

@app.post("/api/platforms/{pid}/schedule")
async def api_update_schedule(pid: int, data: dict = Body(...)):
    return database.update_platform_schedule(pid, data)

@app.get("/api/objects")
async def api_objects():
    return database.get_all_objects()

@app.post("/api/crawl")
async def api_crawl(data: dict = Body(default={})):
    res = await crawler.crawl_object(1)
    return {"success":True, "data":res}

@app.get("/health")
async def health():
    return {"status":"ok"}
