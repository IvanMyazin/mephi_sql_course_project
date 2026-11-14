import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv


class ProjectConfig:
    def __init__(self):
        config_path = Path(__file__).with_name("config.yaml")
        env_path = Path(__file__).with_name(".env")
        load_dotenv(env_path)

        with config_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)

        self.dbname = config["dbname"]
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = config["host"]
        self.port = int(config.get("port", 5432))
        self.schema = config.get("schema", "taxi_project")

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", self.schema):
            raise ValueError("Некорректное имя схемы в config.yaml")
        if not self.user or not self.password:
            raise ValueError("Укажите DB_USER и DB_PASSWORD в файле .env")
