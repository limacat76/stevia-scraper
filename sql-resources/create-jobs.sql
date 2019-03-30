drop table sv_job;

create table sv_job (
    "subreddit" varchar(64) primary key,
    "watermark" varchar(64)
);