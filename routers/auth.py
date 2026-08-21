from datetime import datetime, timezone
from typing import Annotated

import bcrypt

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from models.user import User
from models.tenant import Tenant


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login_page(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={},
    )


@router.post("/login")
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Find user
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .limit(1)
    )

    user = result.scalar_one_or_none()

    # User does not exist
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Invalid username or password"
            },
            status_code=401,
        )

    # User inactive
    if not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "This account is inactive"
            },
            status_code=403,
        )

    # Validate password
    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not password_valid:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Invalid username or password"
            },
            status_code=401,
        )

    # Fetch tenant
    tenant = None

    if user.tenant_id:

        tenant_result = await db.execute(
            select(Tenant)
            .where(Tenant.id == user.tenant_id)
            .limit(1)
        )

        tenant = tenant_result.scalar_one_or_none()

    

    # Clear old session data before creating new session
    request.session.clear()

    # User session data
    request.session["user_id"] = str(user.id)

    request.session["username"] = user.username
    

    request.session["full_name"] = user.full_name
    
    
    request.session["is_admin"] = user.is_admin

    # Tenant session data
    request.session["tenant_id"] = (
        str(user.tenant_id)
        if user.tenant_id
        else None
    )

    request.session["tenant_name"] = (
        tenant.company_name
        if tenant
        else None
    )
   
    request.session["tenant_ntn"] = (
        tenant.ntn_cnic
        if tenant
        else None
    )

    request.session["tenant_province"] = (
            tenant.province 
            if tenant 
            else None
        )

    request.session["tenant_address"] = (
        tenant.address 
        if tenant 
        else None
    )

    # Update login timestamps
    now = datetime.now(timezone.utc)

    user.last_login_at = now
    user.updated_at = now

    await db.commit()

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303,
    )



