-- Create schema for content
CREATE SCHEMA IF NOT EXISTS auth;

-- Create tables with content
CREATE TABLE IF NOT EXISTS auth.user (
    id uuid PRIMARY KEY,
    login text UNIQUE NOT NULL,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    full_name text NOT NULL,
    phone text,
    avatar_link text,
    address text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS auth.group (
    id uuid PRIMARY KEY,
    name text UNIQUE NOT NULL,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS auth.user_group_rel (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    group_id uuid NOT NULL,
    created_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS auth.history (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL,
    user_agent text,
    created_at timestamp with time zone
);