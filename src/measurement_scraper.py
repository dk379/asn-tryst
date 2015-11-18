import time
import random
import netaddr
import MySQLdb
import requests
import operator
import datetime
from multiprocessing import Pool, Process
from ripe.atlas.cousteau import MeasurementRequest, AtlasResultsRequest

DB_HOST = ''
DB_NAME = ''
DB_PASS = ''
POOL = None
INVALID_ASN = 0xffff

def fetch_traceroutes(times):
    """Fetch from atlas a list of Traceroute IDs between the specified
    times. Returns list of IDs"""
    measurement_list = []
    filters = {
        'type': 'traceroute',
        'start_time__gte': datetime.datetime.fromtimestamp(times['start']),
        'start_time__lte': datetime.datetime.fromtimestamp(times['end']),
    }
    measurements = MeasurementRequest(**filters)
    for measurement in measurements:
        if not measurement['stop_time']:
            stop = None
        else:
            stop = datetime.datetime.fromtimestamp(measurement['stop_time'])
        measurement_list.append([
            measurement['id'],
            measurement['description'] or 'No Description',
            datetime.datetime.fromtimestamp(measurement['start_time']),
            stop,
            measurement['interval'],
            measurement['af'],
        ])
    return measurement_list

if __name__ == '__main__':
    POOL = Pool(10)
    now = time.time()
    start_time = 60 *60 * 24 * 365 * 5
    end_time = start_time + 86400
    windows = []
    while end_time >= 86400:
        windows.append({
            'start': now - start_time,
            'end': now - end_time,
        })
        start_time = end_time
        end_time -= 86400
    results = reduce(operator.add,
            [res for res in AS_MAP_POOL.map(fetch_traceroutes, windows) 
                if type(res) == list
            ]
    )
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_NAME,
        passwd=DB_PASS,
        db=DB_NAME
        )
    cur = conn.cursor()
    cur.executemany(
             """REPLACE INTO measurements (msm_id, description, start_time,
             stop_time, interv, af) VALUES (%s, %s, %s, %s, %s, %s)""",
             results
    )
    conn.commit()



