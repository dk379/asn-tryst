
import argparse
import logging
from multiprocessing import Pool
import MySQLdb
import netaddr
import requests
import sys

from read_config import asntryst_read_config


#
# Project specific settings
#
CONFIG = asntryst_read_config()
DB_HOST = CONFIG["database"]["hostname"]
DB_NAME = CONFIG["database"]["database"]
DB_USER = CONFIG["database"]["username"]
DB_PASS = CONFIG["database"]["password"]

INVALID_ASN = 0xffffffff

# IP versions supported
#   4 ... IP version 4
#   6 ... IP version 6
IP_VERSIONS = [4, 6]
# Data call URL for fetching ASN
RIPESTAT_DC_URL = "http://stat.ripe.net/data/network-info/data.json?resource={}"

log = logging.getLogger(__file__)


def is_private_ip(ip):
    """Identifies private IP addresses

    Based on RFC1918 some IP addresses are intended for private use only. 
    If 'ip' is a private IP address True is returned.
    """
    is_private = False
    try:
        ip_parsed = netaddr.IPNetwork(ip)
        is_private = ip_parsed.is_private()
    except netaddr.AddrFormatError, e:
        log.error(e)

    return is_private


def fetch_from_ripestat(url):
    """Result is returned in JSON format, unless in an 
      error case in which it returns None."""
    try:
        response = requests.get(url = url, headers={'Connection':'close'})
	response = response.json()
    except requests.exceptions.RequestException, e:
        log.error(e)
        response = None

    return response

def asn_for_ip(ip):
    """ Returns the ASN looked up on RIPEstat.
    """
    if not is_private_ip(ip):
        json_response = fetch_from_ripestat(RIPESTAT_DC_URL.format(ip))
        try:
            asn = json_response["data"]["asns"][0]
            asn = int(asn)
        except (KeyError,TypeError,IndexError, ValueError), e:
            asn = INVALID_ASN
    else:
        asn = INVALID_ASN

    return asn

MP_POOL = Pool(10)
def asns_for_ips(ips):
    """Returns ip to ASN mapping."""
    asns = MP_POOL.map(asn_for_ip, ips)

    return zip(ips, asns)


def load_asns_for_ips(ip_version=4, fetch_size=10):
    """IPs are fetched from MySQL, looked up on RIPEstat and written back, 
    fetch_size at a time. 
    """
    conn = MySQLdb.connect(host=DB_HOST, 
        user=DB_NAME, passwd=DB_PASS, db=DB_NAME)
    cur = conn.cursor()

    sql = "SELECT COUNT(*) FROM IPSV{} WHERE AUTNUM = 0xffff".format(ip_version)
    cur.execute(sql)
    total = cur.fetchone()[0]

    to_ascii_func = "inet_ntoa" if ip_version ==4 else "inet6_ntoa"
    count = 0
    while( count < total ):
        sql = "SELECT {}(IP) FROM IPSV{} WHERE AUTNUM = 0 limit {}".format(
            to_ascii_func, ip_version, fetch_size)
        cur.execute(sql)
        ips = [ result[0] for result in cur.fetchall() ]

        if not ips:
            break
        else:
            count += len(ips)
            sys.stdout.write(" Progress: {0:.0f}%\r".format( (count*1./total)*100))
            sys.stdout.flush()

        annotated_ips = asns_for_ips(ips)

        to_num_func = "inet_aton" if ip_version == 4 else "inet6_aton"
        insert_sql = "REPLACE INTO IPSV{} (IP,AUTNUM) VALUES ({}(%s),%s)".format(
            ip_version,
            to_num_func)
        values = [ (ip, asn) for ip, asn in annotated_ips ]
        cur.executemany(
            insert_sql, values)
        conn.commit()

    print "Finished: ASN loaded for {} IPs totally".format(count)

    cur.close()
    conn.close()

    return count


def get_parser():
    """Command line parser

      Arguments:
        ip: select IP version to load ASNs for 
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    help_msg = "load ASNs for IP version 4 or 6"
    parser.add_argument("-ip", default=4, choices=IP_VERSIONS, type=int, help=help_msg )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    load_asns_for_ips(args.ip)






   
