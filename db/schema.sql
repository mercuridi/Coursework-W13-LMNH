drop table if exists photo;
drop table if exists reading;
drop table if exists plant;
drop table if exists botanist;
drop table if exists origin;
drop table if exists city;
drop table if exists country;


create table country (
    id int not null identity(1,1),
    country_name varchar,
    primary key (id),
);


create table city (
    id int not null identity(1,1),
    city_name varchar,
    country_id int,
    primary key (id),
    constraint fk_country_city foreign key (country_id) references country (id)
);


create table origin (
    id int not null identity(1,1),
    latitude float,
    longitude float,
    city_id int,
    primary key (id),
    constraint fk_city_origin foreign key (city_id) references city (id)
);


create table botanist (
    id int not null identity(1,1),
    botanist_name varchar,
    botanist_email varchar,
    primary key (id)
);


create table plant (
    id int not null identity(1,1),
    english_name varchar,
    scientific_name varchar,
    origin_id integer,
    primary key (id),
    constraint fk_botanist_plant foreign key (origin_id) references origin (id)
);


create table reading (
    id int not null identity(1,1),
    reading_taken datetime,
    last_watered datetime,
    soil_moisture float,
    soil_temperature float,
    plant_id int,
    botanist_id int,
    primary key (id),
    constraint fk_plant_reading foreign key (plant_id) references plant(id),
    constraint fk_botanist_reading foreign key (botanist_id) references botanist(id)
);


create table photo (
    id int not null identity(1,1),
    plant_id int,
    photo_link varchar,
    primary key (id),
    constraint fk_plant_photo foreign key (plant_id) references plant (id)
);