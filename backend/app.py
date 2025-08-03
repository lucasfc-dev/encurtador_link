from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from contextlib import asynccontextmanager
from config import TORTOISE_CONFIG
from models import Link

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()  
    yield
    await Tortoise.close_connections()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/encurtar_url/")
async def encurtar_link(url: str):
    link = await Link.get_or_none(original_url=url)
    if link is None:
        hashed_url = hash(url)
        link = await Link.create(original_url=str(url), shortened_url=str(hashed_url))
        return link
    else:
        return {"error": "Erro ao encurtar o link."}
    

@app.get('/validar_url/')
async def validar_url(url: str):
    link = await Link.get_or_none(shortened_url=url)
    if link:
        return {"original_url": link.original_url}
    return {"error": "URL inválida ou não encontrada."}

@app.get('/links/')
async def listar_links():   
    links = await Link.all()
    return [{"original_url": link.original_url, "shortened_url": link.shortened_url} for link in links]