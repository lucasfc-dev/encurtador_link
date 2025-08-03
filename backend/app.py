from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from contextlib import asynccontextmanager
from config import TORTOISE_CONFIG,FRONTEND_URL
from models import Link
import hashlib

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()  
    yield
    await Tortoise.close_connections()

app = FastAPI(lifespan=lifespan)

def gerar_codigo_curto(url: str, tamanho: int = 8) -> str:
    hash_sha256 = hashlib.sha256(url.encode()).hexdigest()
    return hash_sha256[:tamanho]

def sanitizar_url(url: str) -> str:
    """
    Apenas adiciona protocolo se não tiver
    Usa HTTP como padrão para maior compatibilidade
    """
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # HTTP como padrão (mais compatível)
    return url

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
    url_sanitizada = sanitizar_url(url)
    
    link = await Link.get_or_none(original_url=url_sanitizada)
    if link is None:
        codigo_curto = gerar_codigo_curto(url_sanitizada)
        url_completa = f"{FRONTEND_URL}/verificadorPag.html?url={codigo_curto}"

        link_existente = await Link.get_or_none(shortened_url=url_completa)
        if link_existente is None:
            link = await Link.create(original_url=url_sanitizada, shortened_url=url_completa)
            return {
                "original_url": link.original_url,
                "shortened_url": link.shortened_url,
                "message": "Link encurtado com sucesso!"
            }
        else:
            return {"error": "Conflito de hash detectado. Tente novamente ou entre em contato com o suporte."}
    else:
        return {
            "original_url": link.original_url,
            "shortened_url": link.shortened_url,
            "message": "Link já foi encurtado anteriormente!"
        }
    

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