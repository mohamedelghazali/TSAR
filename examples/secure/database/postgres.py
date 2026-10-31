"""TSAR reference: secure PostgreSQL access with RLS and parameterized queries."""
import os
import ssl
import asyncpg

TENANT_RLS_SETTING = "app.current_tenant"

class Database:
    def __init__(self, dsn: str, tenant_id: str):
        self._dsn = dsn
        self._tenant_id = tenant_id
        self._pool: asyncpg.Pool | None = None

    async def start(self) -> None:
        ssl_ctx = ssl.create_default_context(cafile="/etc/tls/ca.pem")
        ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        self._pool = await asyncpg.create_pool(
            dsn=self._dsn,
            ssl=ssl_ctx,
            min_size=2,
            max_size=10,
            command_timeout=10,
            server_settings={
                "application_name": "tsar-app",
                "search_path": "app",
                "statement_timeout": "10000",
                "idle_in_transaction_session_timeout": "30000",
            },
        )

    async def stop(self) -> None:
        if self._pool:
            await self._pool.close()

    async def _acquire(self):
        conn = await self._pool.acquire()
        await conn.execute(
            "SELECT set_config($1, $2, true)",
            TENANT_RLS_SETTING, self._tenant_id,
        )
        return conn

    async def get_user(self, user_id: str) -> dict | None:
        async with self._pool.acquire() as conn:
            await conn.execute("SELECT set_config($1, $2, true)",
                               TENANT_RLS_SETTING, self._tenant_id)
            row = await conn.fetchrow(
                "SELECT id, email, created_at FROM app.users WHERE id = $1",
                user_id,
            )
            return dict(row) if row else None

    async def create_order(self, user_id: str, amount_cents: int) -> str:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("SELECT set_config($1, $2, true)",
                                   TENANT_RLS_SETTING, self._tenant_id)
                order_id = await conn.fetchval(
                    "INSERT INTO app.orders (tenant_id, user_id, amount_cents) "
                    "VALUES (current_setting('app.current_tenant')::uuid, $1, $2) "
                    "RETURNING id",
                    user_id, amount_cents,
                )
                return str(order_id)
