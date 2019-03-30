drop table sv_configuration;

create table sv_configuration (
    "key" varchar(64) primary key,
    value varchar(256) not null
);

insert into sv_configuration (key, value) values ('STEVIA_SLEEP_TIME', 2);
insert into sv_configuration (key, value) values ('REDDIT_RATE_LIMIT', 1000);
