import time

from fastapi import FastAPI, HTTPException, Query
from app.api.db import SessionLocal, users_table, bestiaries_table, category_table, entity_table, commentary_table
from sqlalchemy import and_, or_
from fuzzywuzzy import fuzz
import re

from app.api.models import *   # Модели Pydantic для валидации данных
from app.api.sort_models import *
from app.api.including_redis import *


app_v1 = FastAPI(
    title="search API",
    description='''\tRU:
API предоставляет инструменты для поиска и сортировки любого количества бестиариев с любым сдвигом за раз. Доступно несколько типов сортировки, которые можно посмотреть в разделе help, основные будут описаны ниже. 

**Обязательные параметры** для получения поиска: сдвиг и количество бестиариев на одной странице (shift, amount_per_page).

Другие параметры:
* search - строка поиска, ищет по каждому слову отдельно, разделённых через пробел (слово целиком не обязательно), а так же есть возможность включить режим приблизительного поиска (когда слова могут быть написаны с ошибками)
* sort_type - способ сортировки, например by_views (по просмотрам), by_popularity (по популярности) или by_likeness (по сходству)
* search_author - добавляет имя автора в поиск
* hard_register - если True то верхний/нижний регистр имеет значение
* fuzzy_search - если True то это активирует режим примерного поиска (с ошибками)
* reverse - сортировка в обратную сторону


Особенности: при ооочень больших данных этот микросервис может существенно замедлять работу из-за большой обработки каждого бестиария (может стать заметным от 10000+ опубликованных бестиариев)

___

\tEN:
\t\tNONE
    ''',
    version="1.1.0",
)

all_types_sorting = ['by_popularity', 'by_views', 'by_rating', 'by_name', 'by_publication', 'by_last_update', 'by_likeness']
sorting_function_by_type = {
    None: sort_by_popularity,
    'by_popularity': sort_by_popularity,
    'by_views': sort_by_views,
    'by_rating': sort_by_rating,
    'by_name': sort_by_name,
    'by_publication': sort_by_publication,
    'by_last_update': sort_by_last_update,
    'by_likeness': sort_by_likeness
}


def smart_search(query, keys, hard_register=False, fuzzy_search=False):
    if not hard_register:  # Для не строгого регистра
        query = query.lower()

    query_words = query.split()  # Разбиваем запрос на отдельные слова

    matches = []
    for name in keys:
        if not hard_register:
            lower_name = name.lower()
        else:
            lower_name = name

        # Проверяем, содержит ли имя хотя бы одно слово из запроса
        if fuzzy_search:
            # Нечёткий поиск с использованием fuzzywuzzy
            if any(fuzz.partial_ratio(word, lower_name) >= 80 for word in query_words):
                matches.append(name)
        else:
            # Точный поиск
            if any(re.search(re.escape(word), lower_name) for word in query_words):
                matches.append(name)

    return matches


def get_sorted_data(query, data, hard_register: bool, search_author: bool, fuzzy_search: bool):
    dict_data = {}
    for line in data:
        key = line.name
        if search_author:
            key += ' ' + line.author
        dict_data[key] = line

    matches = smart_search(query, dict_data.keys(), hard_register, fuzzy_search)
    return [dict_data[key] for key in matches]


# Получение списка всех бестиариев для пользователя
@app_v1.get("/all_types_sorting/", response_model=List[str], tags=["help"])
def read_bestiaries():
    return all_types_sorting


def sort_result(data, settings):
    if len(data) <= settings.shift:
        return []
    data.sort(key=lambda x: sorting_function_by_type[settings.sort_type](x, settings), reverse=not settings.reverse)
    return data


# Получение бестиария по ID
@app_v1.get("/global_search/", response_model=List[SearchOut], tags=["search"])
def read_bestiary(
    shift: int = Query(..., description="Сдвиг для пагинации"),
    amount_per_page: int = Query(..., description="Количество элементов на странице"),
    search: str = Query('', description="Поисковый запрос"),
    sort_type: str = Query('by_likeness', description="Тип сортировки"),
    search_author: bool = Query(False, description="Поиск по автору"),
    hard_register: bool = Query(False, description="Жесткий регистр"),
    fuzzy_search: bool = Query(True, description="Нечеткий поиск"),
    reverse: bool = Query(False, description="Обратная сортировка")
):
    settings = SearchAndSortGlobal(
        shift=shift,
        amount_per_page=amount_per_page,
        search=search,
        sort_type=sort_type,
        search_author=search_author,
        hard_register=hard_register,
        fuzzy_search=fuzzy_search,
        reverse=reverse
    )

    cached_data = get_cache_from_redis(str(settings), '')
    if cached_data:
        return cached_data[settings.shift:min(settings.shift + settings.amount_per_page, len(cached_data))]
    db = SessionLocal()

    # Запрос
    query = db.query(
        bestiaries_table,  # Все поля из таблицы bestiaries
        users_table.c.username  # Поле name из таблицы users
    ).join(
        users_table,  # Присоединяем таблицу users
        bestiaries_table.c.author == users_table.c.id  # Условие соединения
    ).filter(
        and_(
            bestiaries_table.c.is_published == True,
            bestiaries_table.c.is_deleted == False
        )
    )

    results = query.all()
    print(results)
    if settings.search is not None:
        settings.search = ' '.join(settings.search.split())
    else:
        settings.search = ''
    if settings.search != '':
        results = get_sorted_data(settings.search, results, settings.hard_register, settings.search_author, settings.fuzzy_search)

    results = sort_result(results, settings)

    set_cache(str(settings), '', results)
    return results[settings.shift:min(settings.shift + settings.amount_per_page, len(results))]


if __name__ == '__main__':
    search = SearchAndSortGlobal(shift=0, sort_type='by_likeness', amount_per_page=10, search='андройды  драконов', fuzzy_search=True)

    print(*read_bestiary(search), sep='\n\n')

