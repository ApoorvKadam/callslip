"""Accounts: create one, sign in, sign out, and who is signed in.

Local email-and-password accounts stand in for NYU single sign-on; production would take the
identity from the SSO provider (OIDC) and keep the same `users` row and the same visibility rule.
Passwords are hashed with scrypt. Signing in sets a random token in an HttpOnly, SameSite=Strict
cookie; only its hash is stored, and signing out deletes it. A signed-in user sees the shared
collection plus their own uploads; nobody else sees those uploads.
"""

import asyncio
import base64
import hashlib
import hmac
import logging
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from psycopg import errors
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, StringConstraints
from redis.exceptions import RedisError

from app.api.deps import get_pool

router = APIRouter(prefix="/api/auth", tags=["accounts"])

AUTH_COOKIE = "callslip_auth"
TOKEN_DAYS = 14
# scrypt cost: 16 MB and about 50 ms per hash, run off the event loop.
SCRYPT = {"n": 2**14, "r": 8, "p": 1}

Email = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=254, pattern=r".+@.+")
]
Password = Annotated[str, StringConstraints(min_length=10, max_length=200)]


class Credentials(BaseModel):
    email: Email
    password: Password


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, dklen=32, **SCRYPT)
    return "scrypt$" + "$".join(base64.b64encode(x).decode() for x in (salt, digest))


def check_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
        expected = base64.b64decode(digest)
        actual = hashlib.scrypt(
            password.encode(), salt=base64.b64decode(salt), dklen=len(expected), **SCRYPT
        )
    except ValueError:
        return False
    return hmac.compare_digest(actual, expected)


# Checked against when an email has no account, so a wrong email costs as much as a wrong password.
_NO_ACCOUNT = hash_password(secrets.token_urlsafe(16))


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def viewer(
    request: Request, pool: Annotated[AsyncConnectionPool, Depends(get_pool)]
) -> int | None:
    """The signed-in user's id, or None. Used wherever documents are listed, read or searched."""
    token = request.cookies.get(AUTH_COOKIE)
    if not token:
        return None
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT user_id FROM auth_tokens WHERE token_hash = %s AND expires_at > now()",
            (token_hash(token),),
        )
        row = await cur.fetchone()
    return row[0] if row else None


Viewer = Annotated[int | None, Depends(viewer)]
Pool = Annotated[AsyncConnectionPool, Depends(get_pool)]


async def sign_in(response: Response, request: Request, pool: Pool, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    async with pool.connection() as conn:
        await conn.execute(
            "INSERT INTO auth_tokens (token_hash, user_id, expires_at)"
            " VALUES (%s, %s, now() + %s * interval '1 day')",
            (token_hash(token), user_id, TOKEN_DAYS),
        )
    response.set_cookie(
        AUTH_COOKIE,
        token,
        max_age=TOKEN_DAYS * 86400,
        httponly=True,
        samesite="strict",
        path="/api",
        secure=request.app.state.settings.cookie_secure,
    )


@router.post("/register", status_code=201)
async def register(body: Credentials, request: Request, response: Response, pool: Pool) -> dict:
    password_hash = await asyncio.to_thread(hash_password, body.password)
    try:
        async with pool.connection() as conn:
            cur = await conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (body.email, password_hash),
            )
            user_id = (await cur.fetchone())[0]
    except errors.UniqueViolation:
        raise HTTPException(409, "An account with this email already exists.") from None
    await sign_in(response, request, pool, user_id)
    return {"email": body.email}


log = logging.getLogger(__name__)

# Sign-in attempts are counted in Redis per email and client address, before the password is
# checked: each attempt takes a number in one atomic step, so attempts sent at the same moment
# cannot all slip past the limit. Beyond LOGIN_LIMIT attempts within LOGIN_WINDOW_S of the first,
# that email is refused from that address until the window ends, whatever the password; others
# can still sign in to it, so nobody can lock an account by failing on purpose. A successful
# sign-in clears the count. If Redis is down, sign-in still works.
LOGIN_LIMIT = 5
LOGIN_WINDOW_S = 900
_TAKE_ATTEMPT = """
local n = redis.call('INCR', KEYS[1])
if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return {n, redis.call('TTL', KEYS[1])}
"""


def _failures_key(email: str, address: str) -> str:
    who = f"{email.strip().lower()}|{address}"
    return "login:fail:" + hashlib.sha256(who.encode()).hexdigest()


async def _take_attempt(redis, key: str) -> int:
    """Count this attempt. Returns the seconds to wait when it is over the limit, else 0."""
    try:
        count, ttl = await redis.eval(_TAKE_ATTEMPT, 1, key, LOGIN_WINDOW_S)
    except (RedisError, OSError):
        log.warning("sign-in limit unavailable; not enforced")
        return 0
    return max(int(ttl), 1) if int(count) > LOGIN_LIMIT else 0


async def _clear_attempts(redis, key: str) -> None:
    try:
        await redis.delete(key)
    except (RedisError, OSError):
        log.warning("sign-in limit unavailable; count not cleared")


@router.post("/login")
async def login(body: Credentials, request: Request, response: Response, pool: Pool) -> dict:
    address = request.client.host if request.client else "unknown"
    redis, key = request.app.state.redis, _failures_key(body.email, address)
    wait = await _take_attempt(redis, key)
    if wait:
        raise HTTPException(
            429,
            "Too many failed sign-ins for this email from here. Try again later.",
            headers={"Retry-After": str(wait)},
        )
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT id, email, password_hash FROM users WHERE lower(email) = lower(%s)",
            (body.email,),
        )
        row = await cur.fetchone()
    # The same work and the same answer whether or not the account exists.
    stored = row[2] if row else _NO_ACCOUNT
    ok = await asyncio.to_thread(check_password, body.password, stored)
    if not (row and ok):
        raise HTTPException(401, "The email or the password is not right.")
    await _clear_attempts(redis, key)
    await sign_in(response, request, pool, row[0])
    return {"email": row[1]}


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, pool: Pool) -> None:
    token = request.cookies.get(AUTH_COOKIE)
    if token:
        async with pool.connection() as conn:
            await conn.execute(
                "DELETE FROM auth_tokens WHERE token_hash = %s", (token_hash(token),)
            )
    response.delete_cookie(AUTH_COOKIE, path="/api")


@router.get("/me")
async def me(user: Viewer, pool: Pool) -> dict:
    if user is None:
        return {"email": None}
    async with pool.connection() as conn:
        cur = await conn.execute("SELECT email FROM users WHERE id = %s", (user,))
        row = await cur.fetchone()
    return {"email": row[0] if row else None}
