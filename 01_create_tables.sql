DROP SCHEMA IF EXISTS taxi_project CASCADE;
CREATE SCHEMA taxi_project;

CREATE TABLE taxi_project.vehicles (
    id serial PRIMARY KEY,
    brand varchar(50) NOT NULL CHECK (length(trim(brand)) > 0),
    segment varchar(20) NOT NULL CHECK (segment IN ('эконом', 'комфорт', 'бизнес')),
    registration_number varchar(9) NOT NULL UNIQUE
        CHECK (registration_number ~ '^[АВЕКМНОРСТУХ][0-9]{3}[АВЕКМНОРСТУХ]{2}[0-9]{2,3}$'),
    colour varchar(30) NOT NULL CHECK (length(trim(colour)) > 0),
    prod_year integer NOT NULL
        CHECK (prod_year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1)
);

CREATE TABLE taxi_project.drivers (
    id serial PRIMARY KEY,
    surname varchar(50) NOT NULL CHECK (surname ~ '^[A-Za-zА-Яа-яЁё -]+$'),
    name varchar(50) NOT NULL CHECK (name ~ '^[A-Za-zА-Яа-яЁё -]+$'),
    middle_name varchar(50)
        CHECK (middle_name IS NULL OR middle_name ~ '^[A-Za-zА-Яа-яЁё -]+$'),
    birth_date date NOT NULL
        CHECK (birth_date >= DATE '1900-01-01'
            AND birth_date <= CURRENT_DATE - INTERVAL '18 years'),
    inn char(12) NOT NULL UNIQUE CHECK (inn ~ '^[0-9]{12}$'),
    passport char(10) NOT NULL UNIQUE CHECK (passport ~ '^[0-9]{10}$'),
    vehicle_id integer NOT NULL REFERENCES taxi_project.vehicles(id) ON DELETE CASCADE
);
