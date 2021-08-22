from tinydb import TinyDB, Query
import definition

db = TinyDB(definition.get_path('database/price_db.json'))
price_query = Query()


def insert_to_db(name, price, time):
    if db.get(price_query.coin_name == name) is None:
        return db.insert({'coin_name': name, 'last_price': price, 'time': time})
    else:
        return db.update({'coin_name': name, 'last_price': price, 'time': time}, price_query.coin_name == name)


def read_all_coins(self):
    return db.all()


def get_coin_by_name(name):
    coin = db.get(price_query.coin_name == name)
    return coin
