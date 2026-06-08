-- Seed data
-- User: test@example.com / Qwerty0! (bcrypt, same as backend hash_password)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP TABLE IF EXISTS public.tasks;
DROP TABLE IF EXISTS public.users;
DROP TYPE IF EXISTS public.typetask;
DROP TYPE IF EXISTS public.prioritytask;
DROP TYPE IF EXISTS public.statustask;

CREATE TYPE public.statustask AS ENUM (
    'backlog',
    'to_do',
    'in_progress',
    'on_review',
    'done',
    'cancelled'
);

CREATE TYPE public.prioritytask AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE public.typetask AS ENUM (
    'feature',
    'bug',
    'documentation',
    'other'
);

SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);

CREATE TABLE public.tasks (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    status public.statustask NOT NULL,
    priority public.prioritytask NOT NULL,
    type public.typetask NOT NULL,
    pull_request_url character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

INSERT INTO public.users (id, email, password, name, created_at, updated_at) VALUES
(
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test@example.com',
    '$2b$12$M.gxozcmjorFJ0fvlmAEc.w/UxXZFXjaXZVHHUyX6jOcpNTKOh5WK',
    'Test User',
    '2026-05-07 00:00:00',
    '2026-05-07 00:00:00'
);

INSERT INTO public.tasks (id, user_id, title, description, status, priority, type, pull_request_url, created_at, updated_at) VALUES
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test1',
    'test description',
    'in_progress',
    'high',
    'bug',
    NULL,
    '2026-05-07 00:00:00',
    '2026-05-07 00:00:00'
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a02',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test2',
    NULL,
    'to_do',
    'medium',
    'bug',
    NULL,
    '2026-06-07 00:00:00',
    '2026-06-07 00:00:00'
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a03',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test3',
    NULL,
    'done',
    'low',
    'feature',
    NULL,
    '2026-05-07 00:00:00',
    '2026-05-07 00:00:00'
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a04',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test4',
    NULL,
    'done',
    'low',
    'feature',
    NULL,
    '2026-06-07 00:00:00',
    '2026-06-07 00:00:00'
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a05',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test5',
    NULL,
    'to_do',
    'low',
    'other',
    NULL,
    '2026-05-07 00:00:00',
    '2026-05-07 00:00:00'
);
