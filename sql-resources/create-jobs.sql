-- 000

drop table sv_job;

create table sv_job (
    "subreddit" varchar(64) primary key,
    "watermark" varchar(64)
);

-- 001

alter table sv_job add column "job_type" varchar(64);

alter table sv_job add constraint "sv_job_job_type_not_null" check ("job_type" is not null) not valid;

update sv_job set job_type = 'online';

alter table sv_job validate constraint "sv_job_job_type_not_null";

alter table sv_job add column "threads" integer;
 
alter table sv_job add column "read_threads" integer;