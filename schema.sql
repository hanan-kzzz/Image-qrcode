create extension if not exists pgcrypto;
create table if not exists public.scanlink_images (
  id uuid primary key default gen_random_uuid(),
  title text not null default '',
  target_url text not null,
  features jsonb not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists scanlink_images_active_idx on public.scanlink_images(active);
alter table public.scanlink_images enable row level security;
revoke all on public.scanlink_images from anon, authenticated;
grant all on public.scanlink_images to service_role;
