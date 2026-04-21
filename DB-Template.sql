create table if not exists guildinfo
(
	guildid bigint not null
		constraint guildinfo_pk
		primary key,
	guildname varchar
);

create table if not exists welcome
(
	channel_id bigint,
	guildid bigint not null
		constraint "primary"
		primary key
		constraint welcome_guildid_foreign_key
		references guildinfo,
	welcome_message varchar
);

create table if not exists guildsettings
(
	guildid bigint not null
		constraint "primary"
		primary key
		constraint guildsettings_guildinfo_foreign_key
		references guildinfo,
	prefix varchar default 'i.'::STRING,
	wantslogs boolean default false not null,
	logchannel bigint
);

create table if not exists roles
(
	rolenames varchar,
	reachlevels bigint,
	guildid bigint
		constraint roles_guildid_foreign_key
		references guildinfo,
	is_selfrole boolean default false not null
);

create table if not exists users
(
	userid bigint not null
		primary key,
	username varchar(64)
);

create table if not exists leveling
(
	guildid bigint not null
		constraint leveling_guildid_foreign_key
		references guildinfo,
	userid bigint not null
		constraint leveling_userid_foreign_key
		references users
		on delete cascade,
	xpvalue bigint default 0 not null,
	levelvalue bigint default 0 not null,
	    constraint leveling_userid_guildid_unique
	    unique (userid, guildid)
);

create table if not exists users_bal
(

)

