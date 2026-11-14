from dbtable import DbTable


class VehiclesTable(DbTable):
    table = "vehicles"

    def create(self):
        self.execute("CREATE SCHEMA IF NOT EXISTS " + self.dbconn.schema)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS %s (
                id serial PRIMARY KEY,
                brand varchar(50) NOT NULL CHECK (length(trim(brand)) > 0),
                segment varchar(20) NOT NULL
                    CHECK (segment IN ('эконом', 'комфорт', 'бизнес')),
                registration_number varchar(9) NOT NULL UNIQUE
                    CHECK (registration_number ~ '^[АВЕКМНОРСТУХ][0-9]{3}[АВЕКМНОРСТУХ]{2}[0-9]{2,3}$'),
                colour varchar(30) NOT NULL CHECK (length(trim(colour)) > 0),
                prod_year integer NOT NULL
                    CHECK (prod_year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1)
            )
            """ % self.table_name()
        )

    def drop(self):
        self.execute("DROP TABLE IF EXISTS " + self.table_name())

    def all(self):
        return self.execute(
            """
            SELECT id, brand, segment, registration_number, colour, prod_year
            FROM %s
            ORDER BY id
            """ % self.table_name(),
            fetch="all",
        )

    def insert_one(self, brand, segment, registration_number, colour, prod_year):
        return self.execute(
            """
            INSERT INTO %s (brand, segment, registration_number, colour, prod_year)
            VALUES (%%s, %%s, %%s, %%s, %%s)
            RETURNING id
            """ % self.table_name(),
            (brand, segment, registration_number, colour, prod_year),
            fetch="one",
        )[0]

    def update_one(self, vehicle_id, brand, segment, registration_number, colour, prod_year):
        self.execute(
            """
            UPDATE %s
            SET brand = %%s, segment = %%s, registration_number = %%s,
                colour = %%s, prod_year = %%s
            WHERE id = %%s
            """ % self.table_name(),
            (brand, segment, registration_number, colour, prod_year, vehicle_id),
        )

    def delete_one(self, vehicle_id):
        self.execute(
            "DELETE FROM %s WHERE id = %%s" % self.table_name(),
            (vehicle_id,),
        )
