from datetime import datetime

from tinydb import TinyDB, Query
import definition
from helpers import app_config

db = TinyDB(definition.get_path('database/spammer_db.json'))
spammer = Query()


def save_spammer(user_id, time, period_time):
    if db.get(spammer.id == user_id) is None:
        return db.insert({'id': user_id, 'time': time, 'period_time': period_time})
    else:
        return db.update({'id': user_id, 'time': time, 'period_time': period_time}, spammer.id == user_id)


def get_expired_spammer():
    current_timestamp = datetime.now().timestamp()
    result_set = db.search(spammer.time <= (current_timestamp - app_config.get_config("min_spammer_role_period") * 60))
    result = []

    for r in result_set:
        if r['time'] <= current_timestamp - (r['period_time'] * 60):
            result.append(r)

    return result

def get_all():
    return db.all()


def remove_spammer(id):
    db.remove(spammer.id == id)
