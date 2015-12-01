#!/usr/bin/env python

import sys
import io
import MySQLdb

from read_config import asntryst_read_config

def print_counts(conn):
	databases = [ 'measurements', 'IPV4PAIRS', 'IPV6PAIRS', 'IPSV4', 'IPSV6', 'MIDS' ]
	for db in databases:
		cur = conn.cursor()
		cur.execute('select count(*) from `%s`' % (db))
		results = cur.fetchall()
		for r in results:
			count = r[0]
			print('%-20s %6d' % (db, count))
		cur.close()

def print_traceroute_counts(conn):
	cur = conn.cursor()
	cur.execute('select count(MIDS.msm_id) as count, MIDS.msm_id, measurements.description, measurements.af, DATE(measurements.start_time) as start_date \
			from MIDS \
			left join measurements on MIDS.msm_id = measurements.msm_id \
				group by msm_id \
				order by count desc \
					limit 10')
	results = cur.fetchall()
	print('%5s %8s %1s %9s %s' % ('count', 'msm_id', 'v', 'start_date', 'description'))
	for r in results:
		count = r[0]
		msm_id = r[1]
		description = r[2]
		af = r[3]
		start_date = r[4]
		print('%5s %8s %1s %9s %s' % (count, msm_id, af, start_date, description))
	cur.close()

def main(argv):
	c = asntryst_read_config()
	d = c['database']
	conn = MySQLdb.connect(host=d['hostname'], user=d['username'], passwd=d['password'], db=d['database'])
	print_counts(conn)
	print_traceroute_counts(conn)

	conn.close()

if __name__ == "__main__":
	main(sys.argv[1:])

sys.exit(0)

