from typing import List

from .connector import StoreConnector
from pandas import DataFrame, Series
from datetime import datetime

"""
    В данном модуле реализуется API (Application Programming Interface)
    для взаимодействия с БД с помощью объектов-коннекторов.
    
    ВАЖНО! Методы должны быть названы таким образом, чтобы по названию
    можно было понять выполняемые действия.
"""


def select_all_from_source_files(connector: StoreConnector, city_name: str = "", value_sort: str = "", num_page: int = 0) -> List[tuple]:
    select_cat = f""
    if city_name is not "":
        select_cat = f"WHERE city = {city_name}"

    query = f'SELECT * FROM hotels {select_cat} {value_sort} LIMIT 50 OFFSET {num_page}'
    result = connector.execute(query).fetchall()
    return result


def select_city_from_source_files(connector: StoreConnector) -> List[tuple]:
    query = f'SELECT city FROM hotels'
    result = connector.execute(query).fetchall()
    return result


def sorting_by_price(connector: StoreConnector, str_of_columns: str, value_cat: int = None, value_sort: str = "", str_join: str = '', num_page: int = 0) -> List[tuple]:
    """ Вывод списка обработанных файлов с сортировкой по price в порядке убывания (DESCENDING) """

    select_cat = f""
    if value_cat is not None:
        select_cat = f"WHERE categories.id={value_cat}"

    query = f'SELECT {str_of_columns} FROM rent_real_estate  {str_join} {select_cat} ORDER BY price {value_sort} LIMIT 50 OFFSET {num_page}'
    result = connector.execute(query).fetchall()
    return result


def insert_into_client_base(connector: StoreConnector, name: str = "", email: str = "", password: str = ""):
    """Вставка данных о новых зарегестрированных пользователях в базу данных"""
    query = f'INSERT INTO login_parols (login, parol, email) VALUES (\"{name}\", \"{password}\", \"{email}\")'
    result = connector.execute(query)
    return result


def get_user_login(connector: StoreConnector, email: str = "") -> List[tuple]:
    query = f'SELECT * FROM login_parols WHERE email = \"{email}\"'
    result = connector.execute(query).fetchall()
    return result


def delete_user(connector: StoreConnector, email: str = "") -> List[tuple]:
    query = f'DELETE FROM login_parols WHERE email = \"{email}\"'
    result = connector.execute(query).fetchall()
    return result


def insert_into_source_files(connector: StoreConnector, filename: str):
    """ Вставка в таблицу обработанных файлов """
    now = datetime.now()        # текущая дата и время
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")   # преобразуем в формат SQL
    query = f'INSERT INTO source_files (filename, processed) VALUES (\'{filename}\', \'{date_time}\')'
    result = connector.execute(query)
    return result


def insert_rows_into_processed_data(connector: StoreConnector, dataframe: DataFrame, cities_list, properties_list, localities_list  ):
    """ Вставка строк из DataFrame в БД с привязкой данных к последнему обработанному файлу (по дате) """
    rows = dataframe.to_dict('records')
    files_list = select_all_from_source_files(connector)    # получаем список обработанных файлов
    # т.к. строка БД после выполнения SELECT возвращается в виде объекта tuple, например:
    # row = (1, 'seeds_dataset.csv', '2022-11-15 22:03:16') ,
    # то значение соответствующей колонки можно получить по индексу, например id = row[0]
    last_file_id = files_list[0][0]  # получаем индекс последней записи из таблицы с файлами
    if len(files_list) > 0:
        """for row in rows:
            connector.execute(f'REPLACE INTO property_types (name) VALUES (\'{row["property_type"]}\')')
            connector.execute(f'REPLACE INTO localities (name) VALUES (\'{row["locality"]}\')')
            connector.execute(f'REPLACE INTO cities (name) VALUES (\'{row["city"]}\')')
        for row in rows:
            #connector.execute(f'INSERT INTO processed_data (property_type_ID, locality_ID, city_ID, bedroom, price, area, category, source_file) VALUES ((SELECT id FROM propertys WHERE property_type = \'{row["property_type"]}\'), (SELECT id FROM localitys WHERE locality = \'{row["locality"]}\'), (SELECT id FROM citys WHERE city = \'{row["city"]}\'), \'{row["bedroom"]}\',\'{row["price"]}\',\'{row["area"]}\', (SELECT id FROM categories WHERE id = \'{row["category"]}\'), {last_file_id})')
            connector.execute(f'INSERT INTO processed_data (bedroom, property_type, locality, price, area, city, category, source_file) VALUES (\'{row["bedroom"]}\', (SELECT id FROM property_types WHERE name = \'{row["property_type"]}\'), (SELECT id FROM localities WHERE name = \'{row["locality"]}\'), \'{row["price"]}\',\'{row["area"]}\', (SELECT id FROM cities WHERE name = \'{row["city"]}\'),  (SELECT id FROM categories WHERE id = \'{row["category"]}\'), {last_file_id})')
        """

        for row in rows:
            if get_city_id(row["city"], cities_list) is None:
                    connector.execute(f'INSERT INTO cities (name) VALUES (\'{row["city"]}\')')
                    connector.connection.commit()     
                    cities_list = get_cities_list(connector, cities_list)
            if get_property_type_id(row["property_type"], properties_list) is None:
                    connector.execute(f'INSERT INTO property_types (name) VALUES (\'{row["property_type"]}\')')
                    connector.connection.commit()
                    properties_list = get_properties_list(connector, properties_list)
            if get_locality_id(row["locality"], localities_list) is None:
                    connector.execute(f'INSERT INTO localities (name) VALUES (\'{row["locality"]}\')')
                    connector.connection.commit()
                    localities_list = get_localities_list(connector, localities_list)
        for row in rows:
            prop_id = get_property_type_id(row["property_type"], properties_list)
            loc_id = get_locality_id(row["locality"], localities_list)
            cit_id = get_city_id(row["city"], cities_list)
            #print(f'INSERT INTO rent_real_estate (property_type, locality, city, bedroom, price, area, category, source_file) VALUES ({prop_id}, {loc_id}, {cit_id}, \'{row["bedroom"]}\',\'{row["price"]}\',\'{row["area"]}\', {row["category"]}, {last_file_id})')
            #connector.execute(f'INSERT INTO rent_real_estate (property_type, locality, city, bedroom, price, area, category, source_file) VALUES ((SELECT id FROM property_types WHERE name = \'{row["property_type"]}\'), (SELECT id FROM localities WHERE name = \'{row["locality"]}\'), (SELECT id FROM cities WHERE name = \'{row["city"]}\'), \'{row["bedroom"]}\',\'{row["price"]}\',\'{row["area"]}\', {row["category"]}, {last_file_id})')
            connector.execute(f'INSERT INTO rent_real_estate (property_type, locality, city, bedroom, price, area, category, source_file) VALUES ((SELECT id FROM property_types WHERE name = \'{row["property_type"]}\'), (SELECT id FROM localities WHERE name = \'{row["locality"]}\'), (SELECT id FROM cities WHERE name = \'{row["city"]}\'), \'{row["bedroom"]}\',\'{row["price"]}\',\'{row["area"]}\', (SELECT id FROM categories WHERE id = \'{row["category"]}\'), {last_file_id})')

        """for row in rows:
            connector.execute(f'REPLACE INTO property_types (name) VALUES (\'{row["property_type"]}\')')
            connector.execute(f'REPLACE INTO localities (name) VALUES (\'{row["locality"]}\')')
            connector.execute(f'REPLACE INTO cities (name) VALUES (\'{row["city"]}\')')"""
        """for row in rows:
            
            connector.execute(f'INSERT INTO rent_real_estate (property_type, locality, city, bedroom, price, area, category, source_file) VALUES ((SELECT id FROM property_types WHERE name = \'{row["property_type"]}\'), (SELECT id FROM localities WHERE name = \'{row["locality"]}\'), (SELECT id FROM cities WHERE name = \'{row["city"]}\'), \'{row["bedroom"]}\',\'{row["price"]}\',\'{row["area"]}\', (SELECT id FROM categories WHERE id = \'{row["category"]}\'), {last_file_id})')
        #create(connector, 'rent_real_estate',[1000000000,193011,7558,18453,15,100,10,1,'NULL'])   
        #delete(connector, 'rent_real_estate','id',1000000000)"""
        print('Data was inserted successfully')
    else:
        print('File records not found. Data inserting was canceled.')


def create(connector: StoreConnector, table, values):
    val_str = ''
    for i, value in enumerate(values):
        if i == 0:
            val_str = val_str + f'{value}'
        else:
            val_str = val_str + f',{value}'    

    connector.execute(f'INSERT INTO {table} VALUES ({val_str})')


def read(connector: StoreConnector, table, col, value):
    connector.execute(f'SELECT * FROM {table} WHERE {col} = {value}')


def update(connector: StoreConnector, table, col_values: dict, coln, value):
    query_str = ''
    for i, col in enumerate(col_values.keys()):
        if i == 0:
            query_str = query_str + f'{col} = {col_values[col]}'
        else:    
            query_str = query_str + f', {col} = {col_values[col]}'

    connector.execute(f'UPDATE {table} SET {query_str} WHERE {coln} = {value}')


def delete(connector: StoreConnector, table, col, value):
    connector.execute(f'DELETE FROM {table} WHERE {col} = {value}')


def get_city_id(name, cities_list):
    for i in cities_list:
        if i[1] == name:
            return i[0]
    return None


def get_property_type_id(name, properties_list):
    for i in properties_list:
        if i[1] == name:
            return i[0]
    return None


def get_locality_id(name, localities_list):
    for i in localities_list:
        if i[1] == name:
            return i[0]
    return None        


def get_cities_list(connector: StoreConnector, cities_list):
    cities_list = connector.execute(f'SELECT * FROM cities')
    if cities_list is not None:
        return cities_list.fetchall()
    return []


def get_properties_list(connector: StoreConnector, properties_list):
    properties_list = connector.execute(f'SELECT * FROM property_types')
    if properties_list is not None:
        return properties_list.fetchall()
    return []


def get_localities_list(connector: StoreConnector, localities_list):
    localities_list = connector.execute(f'SELECT * FROM localities')
    if localities_list is not None:
        return localities_list.fetchall()
    return []
