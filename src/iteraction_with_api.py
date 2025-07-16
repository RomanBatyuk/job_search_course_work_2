import requests


def connect_apy():
    """Подключение к api.hh.ru"""
    url = "https://api.hh.ru/vacancies"
    headers = {"User-Agent": "HH-User-Agent"}
    employers_ids = [
        "1047733",
        "1846",
        "2775309",
        "3128158",
        "2302990",
        "48037",
        "10684958",
        "9685659",
        "12035838",
        "3093196",
    ]
    all_vacancies = []

    for employer_id in employers_ids:
        page = 0
        while True:
            params = {"employer_id": employer_id, "page": page, "per_page": 100}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Ошибка! Запрос не выполнен. Статус: {response.status_code}")
                break
            data = response.json()
            all_vacancies.extend(data["items"])
            if data["pages"] <= page + 1:
                break
            page += 1
    return all_vacancies
