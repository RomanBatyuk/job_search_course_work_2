import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.iteraction_with_api import connect_apy
from dotenv import load_dotenv


def create_postgres_db():
    """Подключение к postgres для создания новой БД"""
    load_dotenv()
    password = os.getenv("password")
    conn = psycopg2.connect(
        dbname="postgres", user="postgres", password=password, host="localhost"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Создаем базу, если она еще не существует
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='my_new_db'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("CREATE DATABASE my_new_db")
        print("База данных 'my_new_db' создана.")
    else:
        print("База данных 'my_new_db' уже существует.")

    cursor.close()
    conn.close()


def filling_in_table_organizations():
    """Создание таблицы для организаций и заполнение данными"""
    load_dotenv()
    password = os.getenv("password")
    conn_params = {
        "host": "localhost",
        "database": "my_new_db",
        "user": "postgres",
        "password": password,
    }
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            # Создаем таблицу, если еще не существует
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS organizations (
                    org_id int PRIMARY KEY,
                    org_name varchar(100)
                )
            """
            )
            # Очищаем таблицу перед вставкой
            cur.execute("TRUNCATE TABLE organizations RESTART IDENTITY CASCADE;")
            data = []
            for vacanc in connect_apy():
                vac_data = (vacanc["employer"]["id"], vacanc["employer"]["name"])
                data.append(vac_data)
            # Вставляем с обработкой конфликтов
            cur.executemany(
                "INSERT INTO organizations (org_id, org_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                data,
            )


def filling_in_table_vacancies():
    """Создание таблицы для вакансий и вставка данных с обработкой зарплаты"""
    load_dotenv()
    password = os.getenv("password")

    # параметры подключения к базе данных
    conn_params = {
        "host": "localhost",
        "database": "my_new_db",
        "user": "postgres",
        "password": password,
    }

    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            # Создаем таблицу, если она еще не существует
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vac_id varchar(50) PRIMARY KEY,
                    vac_name varchar(100),
                    salary int DEFAULT 0,
                    link varchar(200),
                    org_id int REFERENCES organizations(org_id) ON DELETE CASCADE
                )
            """
            )

            data = []
            for vacanc in connect_apy():
                # Обработка поля salary с проверкой на None
                salary_info = vacanc.get("salary") or {}
                salary_from = salary_info.get("from")
                salary_to = salary_info.get("to")

                # Обработка зарплаты: среднее, если оба есть; иначе доступное; иначе 0
                if salary_from is not None and salary_to is not None:
                    salary_value = (salary_from + salary_to) / 2
                elif salary_from is not None:
                    salary_value = salary_from
                elif salary_to is not None:
                    salary_value = salary_to
                else:
                    salary_value = 0

                # Преобразуем в целое число (можно оставить float, если нужно)
                salary_int = int(salary_value)

                vac_data = (
                    vacanc["id"],
                    vacanc["name"],
                    vacanc["employer"]["id"],
                    salary_int,
                    vacanc["alternate_url"],
                )
                data.append(vac_data)

            # Вставляем данные в таблицу
            cur.executemany(
                "INSERT INTO vacancies (vac_id, vac_name, org_id, salary, link) VALUES (%s, %s, %s, %s, %s)",
                data,
            )
