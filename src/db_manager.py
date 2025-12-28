import psycopg2
from contextlib import closing
from typing import Dict
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBManager:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(
        self, db_name: str, db_host: str, db_port: str, db_user: str, db_pass: str
    ):
        self.conn_params = {
            "dbname": db_name,
            "user": db_user,
            "password": db_pass,
            "host": db_host,
            "port": db_port,
        }

    def create_database(self) -> None:
        """Создает базу данных PostgreSQL, если она не существует."""
        temp_conn_params = self.conn_params.copy()
        temp_conn_params["dbname"] = "postgres"
        with closing(psycopg2.connect(**temp_conn_params)) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {self.conn_params['dbname']};")

    def create_tables(self) -> None:
        """Создает таблицы для хранения данных о компаниях и вакансиях."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        description TEXT
                    );
                """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        salary INTEGER,
                        link VARCHAR(255),
                        company_id INTEGER REFERENCES companies(id)
                    );
                """
                )
            conn.commit()

    def insert_company(self, company_data: Dict) -> int:
        """Вставляет запись о компании в базу данных."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO companies (name, description) VALUES (%s, %s) RETURNING id;
                    """,
                    (company_data["name"], company_data.get("description")),
                )
                return cur.fetchone()[0]

    def insert_vacancy(self, vacancy_data: Dict, company_id: int) -> None:
        """Вставляет запись о вакансии в базу данных."""
        title = vacancy_data.get("name") or ""
        salary = vacancy_data.get("salary", {}).get("from") or None
        link = vacancy_data.get("alternate_url") or ""

        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vacancies (title, salary, link, company_id) 
                    VALUES (%s, %s, %s, %s);
                    """,
                    (title, salary, link, company_id),
                )
            conn.commit()

    def clear_database(self) -> None:
        """Очищает таблицы в базе данных."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM vacancies;")
                cur.execute("DELETE FROM companies;")
            conn.commit()

    def get_statistics(self) -> Dict:
        """Возвращает статистику по количеству записей."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM companies;")
                num_companies = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM vacancies;")
                num_vacancies = cur.fetchone()[0]
        return {"num_companies": num_companies, "num_vacancies": num_vacancies}
