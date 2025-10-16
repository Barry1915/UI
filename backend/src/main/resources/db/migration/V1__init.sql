-- roles
create table if not exists roles (
    id bigserial primary key,
    code varchar(50) not null unique,
    name varchar(100) not null
);

-- users
create table if not exists users (
    id bigserial primary key,
    username varchar(60) not null unique,
    password_hash varchar(255) not null,
    full_name varchar(100),
    card_number varchar(20) unique,
    phone varchar(20),
    email varchar(100),
    enabled boolean,
    created_at timestamp,
    updated_at timestamp
);

create table if not exists user_roles (
    user_id bigint not null references users(id) on delete cascade,
    role_id bigint not null references roles(id) on delete cascade,
    primary key (user_id, role_id)
);

-- catalog
create table if not exists categories (
    id bigserial primary key,
    name varchar(100) not null unique
);

create table if not exists publishers (
    id bigserial primary key,
    name varchar(150) not null unique
);

create table if not exists books (
    id bigserial primary key,
    title varchar(200) not null,
    author varchar(150),
    isbn varchar(13) unique,
    category_id bigint references categories(id),
    publisher_id bigint references publishers(id),
    publish_date date,
    description varchar(1000),
    total_copies int,
    available_copies int
);

-- circulation
create table if not exists borrow_records (
    id bigserial primary key,
    user_id bigint not null references users(id),
    book_id bigint not null references books(id),
    borrow_date date,
    due_date date,
    return_date date,
    renew_count int
);

create table if not exists reservations (
    id bigserial primary key,
    user_id bigint not null references users(id),
    book_id bigint not null references books(id),
    created_at timestamp,
    expires_at timestamp
);

create table if not exists fine_payments (
    id bigserial primary key,
    user_id bigint not null references users(id),
    amount numeric(10,2),
    reason varchar(255),
    paid_at timestamp
);

-- seed roles
insert into roles(code, name) values
('ADMIN','管理员'),('LIBRARIAN','馆员'),('READER','读者')
ON CONFLICT (code) DO NOTHING;
