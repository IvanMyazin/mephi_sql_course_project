-- Вариант 19


DROP SCHEMA IF EXISTS taxi CASCADE;
CREATE SCHEMA IF NOT EXISTS taxi;


CREATE TABLE IF NOT EXISTS taxi.vehicles (
	id serial PRIMARY KEY,
	brand text NOT NULL, --марка
	segment text NOT NULL, --класс авто
	registration_number text NOT NULL, --госномер
	colour text NOT NULL, --цвет
	prod_year int NOT NULL -- год выпуска
);

CREATE TABLE IF NOT EXISTS taxi.drivers (
	id serial PRIMARY KEY,
	surname text NOT NULL, --фамилия
	name text NOT NULL, --имя
	middle_name text, --отчетсво
	burth_date date NOT NULL, --дата рождения
	inn CHAR(12) NOT NULL UNIQUE CHECK (inn ~ '^[0-9]{12}$'), --инн
	passport CHAR(10) NOT NULL UNIQUE CHECK (passport ~ '^[0-9]{10}$'), -- серия и номер паспорта
	vehicle_id int NOT NULL REFERENCES taxi.vehicles(id)
);

CREATE TABLE IF NOT EXISTS taxi.tariffs (
	id serial PRIMARY KEY,
	name text NOT NULL,
	is_day bool NOT NULL,
	tarrif_type text NOT NULL,
	price_per_km numeric(10, 2) NOT NULL CHECK (price_per_km > 0)
);

CREATE TABLE IF NOT EXISTS taxi.orders(
	id serial PRIMARY KEY,
	date_time timestamp NOT NULL,
	adress text NOT NULL,
	passenger_cnt int CHECK (passenger_cnt  > 0 AND passenger_cnt < 10),
	distance_km NUMERIC (7, 3) NOT NULL CHECK (distance_km > 0),
	driver_id int REFERENCES taxi.drivers(id) 
);

CREATE TABLE IF NOT EXISTS taxi.payments (
	id serial PRIMARY KEY,
	order_id int NOT NULL REFERENCES taxi.orders(id),
	tariff_id int NOT NULL REFERENCES taxi.tariffs(id),
	distance_km NUMERIC (7, 3) NOT NULL CHECK (distance_km > 0),
	amount numeric(10, 2) NOT NULL CHECK (amount > 0),
	CONSTRAINT payments_unique_order_id_tariff_id UNIQUE (order_id, tariff_id)
);
