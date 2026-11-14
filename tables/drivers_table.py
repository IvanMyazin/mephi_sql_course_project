from dbtable import DbTable


class DriversTable(DbTable):
    table = "drivers"

    def create(self):
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS %s (
                id serial PRIMARY KEY,
                surname varchar(50) NOT NULL
                    CHECK (surname ~ '^[A-Za-zА-Яа-яЁё -]+$'),
                name varchar(50) NOT NULL
                    CHECK (name ~ '^[A-Za-zА-Яа-яЁё -]+$'),
                middle_name varchar(50)
                    CHECK (middle_name IS NULL OR middle_name ~ '^[A-Za-zА-Яа-яЁё -]+$'),
                birth_date date NOT NULL
                    CHECK (birth_date >= DATE '1900-01-01'
                        AND birth_date <= CURRENT_DATE - INTERVAL '18 years'),
                inn char(12) NOT NULL UNIQUE CHECK (inn ~ '^[0-9]{12}$'),
                passport char(10) NOT NULL UNIQUE CHECK (passport ~ '^[0-9]{10}$'),
                vehicle_id integer NOT NULL REFERENCES %s(id) ON DELETE CASCADE
            )
            """ % (self.table_name(), self.dbconn.schema + ".vehicles")
        )

    def drop(self):
        self.execute("DROP TABLE IF EXISTS " + self.table_name())

    def all_by_vehicle(self, vehicle_id):
        return self.execute(
            """
            SELECT id, surname, name, middle_name, birth_date, inn, passport
            FROM %s
            WHERE vehicle_id = %%s
            ORDER BY id
            """ % self.table_name(),
            (vehicle_id,),
            fetch="all",
        )

    def count_by_vehicle(self, vehicle_id):
        return self.execute(
            "SELECT COUNT(*) FROM %s WHERE vehicle_id = %%s" % self.table_name(),
            (vehicle_id,),
            fetch="one",
        )[0]

    def insert_one(self, surname, name, middle_name, birth_date, inn, passport, vehicle_id):
        self.execute(
            """
            INSERT INTO %s
                (surname, name, middle_name, birth_date, inn, passport, vehicle_id)
            VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s)
            """ % self.table_name(),
            (surname, name, middle_name, birth_date, inn, passport, vehicle_id),
        )

    def delete_one(self, driver_id):
        self.execute(
            "DELETE FROM %s WHERE id = %%s" % self.table_name(),
            (driver_id,),
        )
