from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_

# URL для подключения к базе данных PostgreSQL
from app.api.identification import DATABASE_URL
url = DATABASE_URL

# Создание подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание объекта MetaData
metadata = MetaData()

# Автоматическая загрузка структуры таблицы users
users_table = Table('users', metadata, autoload_with=engine)
bestiaries_table = Table('bestiaries', metadata, autoload_with=engine)
category_table = Table('categories', metadata, autoload_with=engine)
entity_table = Table('entities', metadata, autoload_with=engine)
commentary_table = Table('commentary', metadata, autoload_with=engine)


# Создание сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Пример использования
if __name__ == "__main__":
    db = SessionLocal()

    query = db.query(
        bestiaries_table,  # Все поля из таблицы bestiaries
        users_table.c.username  # Поле name из таблицы users
    ).join(
        users_table,  # Присоединяем таблицу users
        bestiaries_table.c.author == users_table.c.id  # Условие соединения
    ).filter(
        and_(
            bestiaries_table.c.is_published == False,
            bestiaries_table.c.is_deleted == False
        )
    )

    results = query.all()
    for result in results:
        print(result)

    db.close()