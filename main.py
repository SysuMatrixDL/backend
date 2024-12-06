import os
from fastapi import FastAPI
import api.container as container
import api.login as login
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import multiprocessing

from config import *

app = FastAPI(
    # 似乎这里不生效
    # debug= True if MATRIXDL_ENVIROMENT == "DEVELOPMENT" else False,
    # reload = MATRIXDL_ENVIROMENT == "DEVELOPMENT",
    # host=BACKEND_HOST,
    # port=BACKEND_PORT,
    # worker=int(MATRIXDL_WORKER)
)

origins = [  # for dev
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router, prefix="/api")
app.include_router(container.router,prefix="/containers")

if __name__ == '__main__':
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(
        app,
        debug= True if MATRIXDL_ENVIROMENT == "DEVELOPMENT" else False,
        reload = MATRIXDL_ENVIROMENT == "DEVELOPMENT",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        worker=int(MATRIXDL_WORKER)
    )