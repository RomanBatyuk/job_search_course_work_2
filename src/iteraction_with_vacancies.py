import psycopg2


class DBManager:
    """
    class DBManager - класс который будет подключаться к БД PostgreSQL

    Имеет методы:

    get_companies_with_vacancy_counts - возвращает список компаний и количество вакансий у каждой.
    get_all_vacancies_with_company - возвращает список всех вакансий с названием компании,
    названием вакансии, зарплатой и ссылкой.
    get_average_salary - возвращает среднюю зарплату по вакансиям.
    get_vacancies_above_average_salary - возвращает список вакансий с зарплатой выше средней.
    search_vacancies_by_keyword - возвращает список вакансий с содержанием слова/фразы в названии.
    """

    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def close(self):
        self.conn.close()

    def get_companies_with_vacancy_counts(self):
        """Возвращает список компаний и количество вакансий у каждой."""
        with self.conn.cursor() as cur:
            query = """
                SELECT o.org_name, COUNT(v.vac_id) AS vacancy_count
                FROM organizations o
                LEFT JOIN vacancies v ON o.org_id = v.org_id
                GROUP BY o.org_name;
            """
            cur.execute(query)
            return cur.fetchall()

    def get_all_vacancies_with_company(self):
        """Возвращает список всех вакансий с названием компании, названием вакансии, зарплатой и ссылкой."""
        with self.conn.cursor() as cur:
            query = """
                SELECT v.vac_name, o.org_name, v.salary, v.link
                FROM vacancies v
                JOIN organizations o ON v.org_id = o.org_id;
            """
            cur.execute(query)
            return cur.fetchall()

    def get_average_salary(self):
        """Возвращает среднюю зарплату по вакансиям."""
        with self.conn.cursor() as cur:
            query = "SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL;"
            cur.execute(query)
            result = cur.fetchone()
            return result[0] if result else None

    def get_vacancies_above_average_salary(self):
        """Возвращает список вакансий с зарплатой выше средней."""
        avg_salary = self.get_average_salary()
        if avg_salary is None:
            return []

        with self.conn.cursor() as cur:
            query = """
                SELECT v.vac_name, o.org_name, v.salary, v.link
                FROM vacancies v
                JOIN organizations o ON v.org_id = o.org_id
                WHERE v.salary > %s;
            """
            cur.execute(query, (avg_salary,))
            return cur.fetchall()

    def search_vacancies_by_keyword(self, keyword):
        """Возвращает список вакансий с содержанием слова/фразы в названии."""
        pattern = f"%{keyword}%"
        with self.conn.cursor() as cur:
            query = """
                SELECT v.vac_name, o.org_name, v.salary, v.link
                FROM vacancies v
                JOIN organizations o ON v.org_id = o.org_id
                WHERE v.vac_name ILIKE %s;
            """
            cur.execute(query, (pattern,))
            return cur.fetchall()


def all_functionality():
    """Вспомогательная функция для модуля main.py,
    собирающая в себе весь функционал модуля iteraction_with_vacancies"""
    db_config = {
        "host": "localhost",
        "database": "my_new_db",
        "user": "postgres",
        "password": "43738",
        "port": 5432,
    }

    manager = DBManager(db_config)

    # Получить компании и количество вакансий
    for org_name, count in manager.get_companies_with_vacancy_counts():
        print(f"Компания: {org_name}, вакансий: {count}")

    # Получить все вакансии с названиями компаний
    for vac in manager.get_all_vacancies_with_company():
        print(vac)

    # Средняя зарплата
    print("Средняя зарплата:", manager.get_average_salary())

    # Вакансии с зарплатой выше средней
    for vac in manager.get_vacancies_above_average_salary():
        print(vac)

    # Поиск по ключевому слову (например "python")
    for vac in manager.search_vacancies_by_keyword("Менеджер"):
        print(vac)

    manager.close()
