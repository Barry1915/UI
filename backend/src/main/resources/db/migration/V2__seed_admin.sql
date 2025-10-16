-- seed admin user (password: admin123)
insert into users (username, password_hash, full_name, enabled, created_at, updated_at)
values ('admin', '$2a$10$gF4KJrT1K1W0Bs0Eo4rQweQv2gZt8VbYMrqZQAGq6D0Dg07R.5h5a', '系统管理员', true, now(), now())
ON CONFLICT (username) DO NOTHING;

-- bind admin role
insert into user_roles(user_id, role_id)
select u.id, r.id from users u cross join roles r where u.username='admin' and r.code='ADMIN' on conflict do nothing;
