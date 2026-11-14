class DbTable:
    dbconn = None
    table = ""

    def table_name(self):
        return self.dbconn.schema + "." + self.table

    def execute(self, query, params=(), fetch=None):
        try:
            with self.dbconn.conn.cursor() as cursor:
                cursor.execute(query, params)

                if fetch == "one":
                    result = cursor.fetchone()
                elif fetch == "all":
                    result = cursor.fetchall()
                else:
                    result = None

            self.dbconn.conn.commit()

            return result
        except Exception:
            self.dbconn.conn.rollback()
            raise
