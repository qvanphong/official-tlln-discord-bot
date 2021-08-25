from datetime import datetime

from tinydb import TinyDB, Query
import definition

db = TinyDB(definition.get_path('database/spammer_db.json'))
spammer = Query()


def insert_to_db(user_id, time):
    if db.get(spammer.id == user_id) is None:
        return db.insert({'id': user_id, 'time': time})
    else:
        return db.update({'id': user_id, 'time': time}, spammer.id == user_id)


def spammer_expired_time(expired_second):
    return db.search(spammer.time <= (datetime.now().timestamp() - expired_second))

def remove_spammer(id):
    db.remove(spammer.id == id)