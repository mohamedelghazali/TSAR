-- TSAR reference: RLS-enabled multi-tenant schema.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE app.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE app.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, email)
);

CREATE TABLE app.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES app.tenants(id),
    user_id UUID NOT NULL REFERENCES app.users(id),
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE app.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_tenant_isolation ON app.users
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true)::uuid);

CREATE POLICY orders_tenant_isolation ON app.orders
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true)::uuid);

CREATE ROLE tsar_app NOLOGIN;
GRANT USAGE ON SCHEMA app TO tsar_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.users, app.orders TO tsar_app;
GRANT SELECT ON app.tenants TO tsar_app;

ALTER ROLE tsar_app SET search_path = app;
ALTER ROLE tsar_app SET statement_timeout = '10s';
ALTER ROLE tsar_app SET idle_in_transaction_session_timeout = '30s';
