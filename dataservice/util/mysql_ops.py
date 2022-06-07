import pymysql.cursors
from itertools import chain, islice
import util.socket_ops as socket_ops
from config.config import DATA_INSERT_UPDATE_START_PROGRESS, DATA_INSERT_UPDATE_END_PROGRESS, MYSQL_INSERT_BATCH_SIZE


def new_conn():
    conn = pymysql.connect(host='mysql-srv', user='root', port=3306,
                           db='test', cursorclass=pymysql.cursors.DictCursor)
    return conn


def num_of_data():
    sql = '''
    SELECT COUNT(*) AS cnt
    FROM orders
    '''
    result = _exec(sql)[0]
    return result


def retrieve_data(limit, offset):
    sql = '''
    SELECT * FROM orders
    LIMIT %s OFFSET %s 
    '''
    results = _exec(sql, (limit, offset, ))
    return results


def update_insert_df(df, notifier, room):
    conn = new_conn()
    try:
        with conn.cursor() as cursor:
            sql = '''
            INSERT INTO orders (order_id, region, country, item_type, sales_channel, order_priority,
            order_date, ship_date, units_sold, unit_price, unit_cost, total_revenue, total_cost, total_profit, nric) VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            region = VALUES(region),
            country = VALUES(country),
            item_type = VALUES(item_type),
            sales_channel = VALUES(sales_channel),
            order_priority = VALUES(order_priority),
            order_date = VALUES(order_date),
            ship_date = VALUES(ship_date),
            units_sold = VALUES(units_sold),
            unit_price = VALUES(unit_price),
            unit_cost = VALUES(unit_cost),
            total_revenue = VALUES(total_revenue),
            total_cost = VALUES(total_cost),
            total_profit = VALUES(total_profit),
            nric = VALUES(nric)
            '''
            num_to_be_update_insert = df.shape[0]
            values = ((row.order_id, row.region, row.country, row.item_type, row.sales_channel, row.order_priority,
                       row.order_date.date(),
                       row.ship_date.date(), row.units_sold, row.unit_price, row.unit_cost, row.total_revenue, row.total_cost,
                       row.total_profit, row.nric) for _, row in df.iterrows())
            print('prepare to insert data to db')

            affected_rows_acc = 0
            processed_rows_acc = 0
            for chunk in _chunks(values, size=MYSQL_INSERT_BATCH_SIZE):
                batch_values = list(chunk)
                cursor.executemany(sql, batch_values)
                conn.commit()
                affected_rows_acc += cursor.rowcount
                processed_rows_acc += len(batch_values)
                progress = DATA_INSERT_UPDATE_START_PROGRESS + \
                    (DATA_INSERT_UPDATE_END_PROGRESS - DATA_INSERT_UPDATE_START_PROGRESS) * \
                    (processed_rows_acc / num_to_be_update_insert)
                print('data isnert progress = ', progress, ' room = ', room)
                socket_ops.notify_client(notifier, progress=progress, status='processing',
                                         room=room, details='inserting(updating) data...')
            print('insert finsihed')
            return affected_rows_acc
    except Exception as e:
        raise e
    finally:
        conn.close()


def _exec(sql, param_tuple=None):
    conn = new_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, param_tuple)
            return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        conn.close()


def _chunks(iterable, size=5000):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))
