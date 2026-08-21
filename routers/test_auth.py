# test_auth_flow.py

import asyncio
import os

import bcrypt
from dotenv import load_dotenv

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models.user import User
from models.tenant import Tenant


# --------------------------------------------------
# Load environment
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")


# --------------------------------------------------
# Database
# --------------------------------------------------

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# --------------------------------------------------
# Test login
# --------------------------------------------------

async def test_login(username: str, password: str):

    async with SessionLocal() as db:

        # ------------------------------------------
        # Find user
        # ------------------------------------------

        result = await db.execute(
            select(User)
            .where(User.username == username)
            .limit(1)
        )

        user = result.scalar_one_or_none()

        if not user:
            print("\nUSER NOT FOUND")
            return

        print("\n========== USER ==========")

        print("User ID:", user.id)
        print("Username:", repr(user.username))
        print("Full Name:", repr(user.full_name))
        print("Tenant ID:", user.tenant_id)
        print("Active:", user.is_active)
        print("Admin:", user.is_admin)

        # ------------------------------------------
        # Validate password
        # ------------------------------------------

        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )

        print("\nPassword valid:", password_valid)

        if not password_valid:
            print("LOGIN FAILED")
            return

        # ------------------------------------------
        # Fetch tenant
        # ------------------------------------------

        tenant = None

        if user.tenant_id:

            tenant_result = await db.execute(
                select(Tenant)
                .where(Tenant.id == user.tenant_id)
                .limit(1)
            )

            tenant = tenant_result.scalar_one_or_none()

        print("\n========== TENANT ==========")

        if tenant:

            print("Tenant ID:", tenant.id)
            print("Company:", repr(tenant.company_name))
            print("NTN:", repr(tenant.ntn_cnic))
            print("Province:", repr(tenant.province))
            print("City:", repr(tenant.city))
            print("Address:", repr(tenant.address))

        else:

            print("TENANT NOT FOUND")

        # ------------------------------------------
        # Simulate session
        # ------------------------------------------

        session = {}

        session["user_id"] = str(user.id)
        session["username"] = user.username
        session["full_name"] = user.full_name
        session["is_admin"] = user.is_admin

        session["tenant_id"] = (
            str(user.tenant_id)
            if user.tenant_id
            else None
        )

        session["tenant_name"] = (
            tenant.company_name
            if tenant
            else None
        )

        session["tenant_ntn"] = (
            tenant.ntn_cnic
            if tenant
            else None
        )

        session["tenant_province"] = (
            tenant.province
            if tenant
            else None
        )

        session["tenant_address"] = (
            tenant.address
            if tenant
            else None
        )

        # ------------------------------------------
        # Print simulated session
        # ------------------------------------------

        print("\n========== SESSION ==========")

        for key, value in session.items():
            print(f"{key}: {repr(value)}")

        print("\n========== IMPORTANT ==========")

        print(
            "tenant_province:",
            repr(session.get("tenant_province")),
        )

        print(
            "tenant_address:",
            repr(session.get("tenant_address")),
        )


# --------------------------------------------------
# Run
# --------------------------------------------------

async def main():

    username = input("Username: ")
    password = input("Password: ")

    await test_login(
        username=username,
        password=password,
    )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())