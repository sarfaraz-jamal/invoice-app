"""
FBR Invoice App — FastAPI entry point
Wires up all routers. DB models and FBR service go in separate modules.
"""

import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from routers import auth, invoices, fbr_reference


app = FastAPI(
    title="GOAT Invoice — FBR Integrated",
    version="1.0.0"
)


# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET",
        "change-this-in-production"
    )
)


# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# Templates
templates = Jinja2Templates(
    directory="templates"
)


# Routers
app.include_router(
    invoices.router,
    prefix="/invoices"
)

app.include_router(auth.router)

app.include_router(fbr_reference.router)


# Home page
@app.get("/")
async def home(request: Request):

    # User not logged in
    if not request.session.get("user_id"):
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # User logged in
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "user": {
                "id": request.session.get("user_id"),
                "username": request.session.get("username"),
                "full_name": request.session.get("full_name"),
                "tenant_id": request.session.get("tenant_id"),
                "is_admin": request.session.get("is_admin"),
            }
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )