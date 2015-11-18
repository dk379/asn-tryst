import time
import random
import netaddr
import MySQLdb
import requests
import datetime
from multiprocessing import Pool, Process
from ripe.atlas.cousteau import MeasurementRequest, AtlasResultsRequest

DB_HOST = ''
DB_NAME = ''
DB_PASS = ''
AS_MAP_POOL = None
PARSE_POOL = None
INVALID_ASN = 0xffff

def parse_traceroute(msm_id, start, end):
    """Given a measurement ID, pull down the traceroute results and parse
    out all the IPS. Returns a list of IP addreesses"""
    traceroutes = []
    filters = {
        'msm_id': msm_id,
        'start': datetime.datetime.fromtimestamp(start),
        'stop': datetime.datetime.fromtimestamp(end),
    }
    is_success, results = AtlasResultsRequest(**filters).create()
    if is_success:
        for trace_result in results:
            hops = []
            for hop in trace_result['result']:
                if 'result' in hop:
                    hops.append(hop['result'][0].get('from', ''))
            traceroutes.append((hops, trace_result['timestamp']))
    return traceroutes


def add_ip_to_database(traces, family):
    ips = set()
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_NAME,
        passwd=DB_PASS,
        db=DB_NAME,
    )
    cur = conn.cursor()
    cur.execute('select msm_id, af from measurements')
    results = cur.fetchall()
    for trace in traces:
        for ip in trace[0]:
            if ip == '' or is_private_ip(ip):
                continue
            else:
                ips.add(ip)
    if '' in ips:
        ips.remove('')
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_NAME,
        passwd=DB_PASS,
        db=DB_NAME,
    )
    cur = conn.cursor()
    if family == 4:
        table = 'IPSV4'
        function = 'inet_aton'
    elif family == 6:
        table = 'IPSV6'
        function = 'inet6_aton'
    cur.executemany(
             """REPLACE INTO {} (IP) VALUES ({}(%s))""".format(table, function),
             ips
    )
    conn.commit()

def is_private_ip(ip):
    """Checks for private IP space according to RFC1918. Returns boolean"""
    is_private = False
    try:
        ip_parsed = netaddr.IPNetwork(ip)
        is_private = ip_parsed.is_private()
    except netaddr.AddrFormatError, e:
        print e

    return is_private


def fetch_from_ripestat(url):
    """Result is returned in JSON format, unless in an
      error case in which it returns None."""
    try:
        response = requests.get(url = url, headers={'Connection':'close'})
        response = response.json()
    except requests.exceptions.RequestException, e:
        response = None

    return response

def asn_for_ip(ip):
    """ Returns the ASN looked up on RIPEstat. On look-up failures
    it is retried, once."""
    template_url = "http://stat.ripe.net/data/network-info/data.json?resource={}"

    if not is_private_ip(ip):
        json_response = fetch_from_ripestat(template_url.format(ip))
        i = 3
        while(not json_response and i > 0):
            i -= 1
            json_response = fetch_from_ripestat(template_url.format(ip))

        try:
            asn = json_response["data"]["asns"][0]
        except (KeyError,TypeError,IndexError, ValueError), e:
            asn = INVALID_ASN

        try:
            asn = int(asn)
        except ValueError, e:
            asn = INVALID_ASN
    else:
        asn = INVALID_ASN

    return asn

def asns_for_ips(ips):
    """Returns ip to ASN mapping."""
    asns = MP_POOL.map(asn_for_ip, ips)

    return zip(ips, asns)


def annotate_ips(ip_version="V4", max_runs = 10):
    """Annotates the IPs with ASNS.

    mysql> select IP, INET_NTOA(IP) from IPSV4 WHERE AUTNUM = 0 order by IP limit 10;

    """
    conn = MySQLdb.connect(host=DB_HOST, 
        user=DB_NAME, passwd=DB_PASS, db=DB_NAME)
    cur = conn.cursor()

    count = 0
    idx = 0
    while(idx < max_runs):
        idx += 1
        # get ips to annotate
        sql = "SELECT INET_NTOA(IP) FROM IPS{} WHERE AUTNUM = 0 limit 20".format(ip_version.upper())
        cur.execute(sql)
        ips = [ result[0] for result in cur.fetchall() ]

        # leave if annotation is done
        if not ips:
            print "Done: {} IPs annoted totally".format(count)
            break
        else:
            count += len(ips)

        annotated_ips = asns_for_ips(ips)

        # write back to database table
        to_num_func = "inet_aton" if "V4" in ip_version else "inet6_aton"
        insert_sql = "REPLACE INTO IPS{} (IP,AUTNUM) VALUES ({}(%s),%s)".format(
            ip_version.upper(),
            to_num_func)
        values = [ (ip, asn) for ip, asn in annotated_ips ]
        print values
        cur.executemany(
            insert_sql, values)
        conn.commit()
        print "{} IPs updated in DB".format(len(values))

    cur.close()
    conn.close()

    return count

def find_pairs(as_map, time, af, msm_id):
    """Given a traceroute, find out the boundary pairs and add to the database"""
    table = 'IPV4PAIRS'
    function = 'inet_aton'
    if af == 6:
        table = 'IPV6PAIRS'
        function = 'inet6_aton'
    pairs = []
    last_ip = None
    last_asn = None
    for ip, asn in as_map:
        if last_ip and last_asn:
            if last_asn != INVALID_ASN and asn != INVALID_ASN and last_asn != asn:
                # OK, this is a real pair
                pairs.append({
                    'ip1': last_ip,
                    'ip2': ip,
                    'as1': last_asn,
                    'as2': asn,
                    'time': time,
                })
        last_ip = ip
        last_asn = asn
    conn = MySQLdb.connect(host=DB_HOST, user=DB_NAME, passwd=DB_PASS, db=DB_NAME)
    for pair in pairs:
        cur = conn.cursor()
        ips = tuple(sorted([pair['ip1'], pair['ip2']]))
        cur.execute('REPLACE into {} (IP1, IP2) values ({}(%s), {}(%s))'.format(table, function, function),
            ips
        )
        pair_id = cur.lastrowid
        cur.execute('REPLACE into MIDS (PAIR_ID, msm_id, timestamp, af) values (%s, %s, %s, %s)',
                (pair_id, msm_id, datetime.datetime.fromtimestamp(time), af)
        )
        conn.commit()

def main():
    conn = MySQLdb.connect(host=DB_HOST, user=DB_NAME, passwd=DB_PASS, db=DB_NAME)
    cur = conn.cursor()
    cur.execute('select msm_id, af from measurements order by msm_id desc')
    results = list(cur.fetchall())
    random.shuffle(results)
    for result in results:
        traces = parse_traceroute(result[0], time.time() - 86400, time.time())
        add_ip_to_database(traces, result[1])
        for trace in traces:
            ip_asn_map = asns_for_ips(trace[0])
            find_pairs(ip_asn_map, trace[1], result[1], result[0])
    annotate_ips(ip_version="V4")
    annotate_ips(ip_version="V6")


if __name__ == '__main__':
    MP_POOL = Pool(10)
    main()

