drop table if exists botanist cascade;
drop table if exists plant cascade;
drop table if exists reading cascade;
drop table if exists origin cascade;
drop table if exists city cascade;
drop table if exists country cascade;
drop table if exists photo cascade;

create table botanist (
    id int generated always as identity,
    botanist_name varchar,
    botanist_email varchar,
    primary key (id)
);

create table plant (
    id int generated always as identity,
    english_name varchar,
    scientific_name varchar,
    origin_id integer,
    primary key (id),
    foreign key (origin_id) references origin (id)
);

create table reading (
    id int generated always as identity,
    reading_taken timestamp,
    last_watered timestamp,
    soil_moisture float,
    soil_temperature float,
    plant_id int,
    botanist_id int,
    primary key (id),
    foreign key (plant_id) references plant (id),
    foreign key (botanist_id) references botanist (id)
);

create table origin (
    id int generated always as identity,
    latitude float,
    longitude float,
    city_id int,
    primary key (id)
    foreign key (city_id) references city (id)
);

create table city (
    id int generated always as identity,
    city_name varchar,
    country_id int,
    primary key (id),
    foreign key (country_id) references country (id)
);

create table country (
    id int generated always as identity,
    country_name varchar,
    primary key (id),
);

create table photo (
    id int generated always as identity,
    plant_id int,
    photo_link varchar,
    primary key (id)
    foreign key (plant_id) references plant (id)
);