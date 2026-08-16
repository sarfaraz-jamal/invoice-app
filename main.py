"""
FBR Invoice App — FastAPI entry point
Wires up all routers. DB models and FBR service go in separate modules.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from routers import invoices


app = FastAPI(title="GOAT Invoice — FBR Integrated", version="1.0.0")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# ── Routers (import once you scaffold each module) ──────────────────────────
# from routers import auth, invoices, customers, products, reports, settings, fbr, tenants
# app.include_router(auth.router,      prefix="/auth",      tags=["auth"])
# app.include_router(tenants.router,   prefix="/tenants",   tags=["tenants"])
app.include_router(invoices.router,  
                   prefix="/invoices")
# app.include_router(customers.router, prefix="/customers", tags=["customers"])
# app.include_router(products.router,  prefix="/products",  tags=["products"])
# app.include_router(reports.router,   prefix="/reports",   tags=["reports"])
# app.include_router(settings.router,  prefix="/settings",  tags=["settings"])
# app.include_router(fbr.router,       prefix="/fbr",       tags=["fbr"])

# Home page
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="base.html"
    )



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
