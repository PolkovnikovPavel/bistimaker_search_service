import requests


url = "http://127.0.0.1:6601/search-service/api/v1/global_search/"
# url = "http://bistimaker.ru/search-service/api/v1/global_search/"

# TODO Сделать нормальные тесты

# data = {
#     "shift": 0,
#     "amount_per_page": 10,
#     "search": 'егор',
#     "fuzzy_search": True,
#     "sort_type": 'by_likeness'
# }
# response = requests.get(url, json=data)
# try:
#     print(*response.json(), sep='\n')
# except Exception:
#     print(response)


response = requests.get('http://127.0.0.1:6601/search-service/api/v1/global_search/?shift=0&amount_per_page=20')
try:
    print(*response.json(), sep='\n')
except Exception:
    print(response)




