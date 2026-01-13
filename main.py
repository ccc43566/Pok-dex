import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="宝可梦图鉴 API")


