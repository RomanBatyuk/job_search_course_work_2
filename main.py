from src.iteraction_with_file import create_postgres_db, filling_in_table_organizations, filling_in_table_vacancies
from src.iteraction_with_vacancies import all_functionality


def main_function():
    """Главная функция, охватывающая весь функционал проекта"""
    create_postgres_db()
    filling_in_table_organizations()
    filling_in_table_vacancies()
    all_functionality()

if __name__ == "__main__":
    main_function()