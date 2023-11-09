create table if not exists guildinfo
(
    guildid   bigint not null
        constraint guildinfo_pk
            primary key,
    guildname varchar
);

-- can use this if you don't have root acces, just uncomment
-- alter table guildinfo
--     owner to <user>;

create table if not exists leveling
(
    guildid    bigint           not null
        constraint leveling_fk
            references guildinfo,
    userid     bigint           not null,
    username   varchar,
    xpvalue    bigint default 0 not null,
    levelvalue bigint default 0 not null
);

-- alter table leveling
--     owner to <user>;

create table if not exists welcome
(
    channel_id      bigint,
    guildid         bigint
        constraint welcome_fk
            references guildinfo,
    welcome_message varchar
);

-- alter table welcome
--     owner to <user>;

create table if not exists guildsettings
(
    guildid    bigint                not null
        constraint guildsettings_fk
            references guildinfo,
    prefix     varchar default 'i.'::STRING,
    wantslogs  boolean default false not null,
    logchannel bigint
);

-- alter table guildsettings
--     owner to <user>;

create table if not exists roles
(
    guildname   varchar,
    rolenames   varchar,
    reachlevels bigint,
    guildid     bigint
        constraint roles_fk
            references guildinfo,
    is_selfrole boolean default false not null
);

-- alter table roles
--     owner to <user>;
