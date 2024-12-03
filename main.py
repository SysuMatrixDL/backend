from fastapi import FastAPI
import route.login as login

app = FastAPI(debug=True)
app.include_router(login.router, prefix="")
