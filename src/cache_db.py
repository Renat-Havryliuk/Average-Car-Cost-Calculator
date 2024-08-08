import time
from contextlib import contextmanager
import sqlite3


@contextmanager
def connecting(update_flag=False):
    try:
        conn = sqlite3.connect("D:/Python/CarPricesScrapers/data/prices_cache.db")
        cursor = conn.cursor()
        yield cursor
        if update_flag is True:
            conn.commit()
    except Exception as _ex:
        print(_ex)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def cache_table_creating():
    with connecting(True) as cursor:
        cursor.execute('''
        CREATE TABLE Cars_Prices(
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            area TEXT,
            years TEXT,
            average_price REAL NOT NULL,
            currency TEXT NOT NULL,
            timestamp INTEGER DEFAULT (strftime('%s', 'now'))
        );
        ''')


def index_creating():
    with connecting(True) as cursor:
        cursor.execute('''
        CREATE INDEX index_params
        ON Cars_Prices (brand, model, area, years, currency)
        ''')


# This function searches data in the table
def data_searching_in_the_cache(car_brand, car_model, area, interval, currency):
    with connecting() as cursor:
        query = '''
                SELECT average_price, timestamp FROM Cars_Prices
                WHERE brand = ? AND model = ? AND area = ? AND years = ? AND currency = ?;
                '''
        cursor.execute(query, (car_brand,
                               car_model,
                               area if area != "0" else None,
                               interval if interval != "0" else None,
                               currency))
        results = cursor.fetchall()
        if len(results) == 1:
            average_price, timestamp = results[0]
            if int(time.time()) - timestamp < 86_400:
                return int(average_price), 0
            else:
                return 0, 1
        else:
            return 0, 2


# This function updates data from the table
def data_updating_into_the_cache(average_price, car_brand, car_model, area, interval, currency):
    with connecting(True) as cursor:
        query = '''
                UPDATE Cars_Prices
                SET average_price = ?, timestamp = (strftime('%s', 'now'))
                WHERE brand = ? AND model = ? AND area = ? AND years = ? AND currency = ?;
                '''
        cursor.execute(query, (average_price,
                               car_brand,
                               car_model,
                               area if area != "0" else None,
                               interval if interval != "0" else None,
                               currency))


# This function adds data into the table
def data_adding_into_the_cache(average_price, car_brand, car_model, area, interval, currency):
    with connecting(True) as cursor:
        query = '''
                INSERT INTO Cars_Prices(average_price, brand, model, area, years, currency)
                VALUES (?, ?, ?, ?, ?, ?);
                '''
        cursor.execute(query, (average_price,
                               car_brand,
                               car_model,
                               area if area != "0" else None,
                               interval if interval != "0" else None,
                               currency))


# This function deletes old cache entries
def old_data_deleting_from_the_cache():
    with connecting(True) as cursor:
        cursor.execute('''
        DELETE FROM Cars_Prices
        WHERE timestamp <= strftime('%s', 'now') - 86400;
        ''')


# This function creates the table and the index
def main():
    cache_table_creating()
    index_creating()


if __name__ == "__main__":
    main()
