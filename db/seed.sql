insert into country (country_name) values ('Andromeda');
insert into country (country_name) values ('Orion');

insert into city (city_name, country_id) values ('Alpheratz', (select id from country where country_name = 'Andromeda'));
insert into city (city_name, country_id) values ('Horsehead', (select id from country where country_name = 'Orion'));

insert into origin (longitude, latitude, city_id) values (0.5, -0.5, (select id from city where city_name = 'Alpheratz'));
insert into origin (longitude, latitude, city_id) values (1.5, -1.5, (select id from city where city_name = 'Horsehead'));

insert into plant (english_name, scientific_name, origin_id) values ('Akuze Wildflower', 'Wildflower from Akuze', (select id from origin where longitude = 0.5));
insert into plant (english_name, scientific_name, origin_id) values ('Hades Flytrap', 'Named after a Greek god, obviously', (select id from origin where longitude = 1.5));

insert into photo (photo_link, plant_id) values ('Web link 1', (select id from plant where english_name = 'Akuze Wildflower'));
insert into photo (photo_link, plant_id) values ('Web link 2', (select id from plant where english_name = 'Hades Flytrap'));

insert into botanist (
	botanist_name,
	botanist_email,
	botanist_phone
) values (
	'Garrus Vakarian',
	'Serious Email 1',
	'Serious Phone Number 1'
);

insert into botanist (
	botanist_name,
	botanist_email,
	botanist_phone
) values (
	'Mordin Solus',
	'Serious Email 2',
	'Serious Phone Number 2'
);

insert into reading(soil_moisture, soil_temperature, plant_id, botanist_id) values (0.85, 0.35, (select id from plant where english_name = 'Akuze Wildflower'), (select id from botanist where botanist_name = 'Garrus Vakarian'));
insert into reading(soil_moisture, soil_temperature, plant_id, botanist_id) values (1.85, 1.35, (select id from plant where english_name = 'Hades Flytrap'), (select id from botanist where botanist_name = 'Mordin Solus'));

