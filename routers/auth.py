from typing import Annotated

import bcrypt

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg import Connection

from db.connection import get_connection


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(request: Request):

    # Already logged in
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={}
    )


@router.post("/login")
def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    connection: Annotated[Connection, Depends(get_connection)],
):

    user = connection.execute(
        """
        SELECT
            id,
            tenant_id,
            username,
            full_name,
            password_hash,
            is_active,
            is_admin
        FROM users
        WHERE username = %s
        LIMIT 1
        """,
        (username,)
    ).fetchone()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Invalid username or password"
            },
            status_code=401
        )

    if not user["is_active"]:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "This account is inactive"
            },
            status_code=403
        )

    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_valid:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "error": "Invalid username or password"
            },
            status_code=401
        )

    request.session["user_id"] = str(user["id"])

    request.session["tenant_id"] = (
        str(user["tenant_id"])
        if user["tenant_id"]
        else None
    )

    request.session["username"] = user["username"]
    request.session["full_name"] = user["full_name"]
    request.session["is_admin"] = user["is_admin"]

    connection.execute(
        """
        UPDATE users
        SET
            last_login_at = NOW(),
            updated_at = NOW()
        WHERE id = %s
        """,
        (user["id"],)
    )

    connection.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )