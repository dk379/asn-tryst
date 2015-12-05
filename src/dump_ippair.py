#!/usr/bin/env python

import sys
import json
import os
import getopt

import MySQLdb
import requests

from read_config import asntryst_read_config

verbose = 0

def collect_geo(conn, af_list):
	ip_geo = {}

	for af in af_list:
		if af == 6:
			inet_ntoa = 'INET6_NTOA'
		else:
			inet_ntoa = 'INET_NTOA'
		## IP1
		cur = conn.cursor()
		cur.execute('select %s(IPV%dPAIRS.IP1), lon, lat, place, hostname \
				from IPV%dPAIRS \
				  join `openipmap_locations` on `openipmap_locations`.ip = IPV%dPAIRS.IP1 \
				    where lon != 0.0 and lat != 0.0' % (inet_ntoa, af, af, af))

		results = cur.fetchall()
		for r in results:
			ip = r[0]
			lon = r[1]
			lat = r[2]
			place = r[3]
			hostname = r[4]
			if ip not in ip_geo:
				ip_geo[ip] = {'lon': float(lon), 'lat': float(lat), 'place': place, 'hostname': hostname};

		cur.close()

		## IP2
		cur = conn.cursor()
		cur.execute('select %s(IPV%dPAIRS.IP2), lon, lat, place, hostname \
				from IPV%dPAIRS \
				  join `openipmap_locations` on `openipmap_locations`.ip = IPV%dPAIRS.IP2 \
				    where lon != 0.0 and lat != 0.0' % (inet_ntoa, af, af, af))

		results = cur.fetchall()
		for r in results:
			ip = r[0]
			lon = r[1]
			lat = r[2]
			place = r[3]
			hostname = r[4]
			if ip not in ip_geo:
				ip_geo[ip] = {'lon': float(lon), 'lat': float(lat), 'place': place, 'hostname': hostname};

		cur.close()

	return ip_geo

def asntryst_get_ip_pairs(conn, af_list, asn1, asn2):
	global verbose

	pairs = []
	asns = {}
	asns_unknown = {}

	for af in af_list:
		if af == 6:
			inet_ntoa = 'INET6_NTOA'
		else:
			inet_ntoa = 'INET_NTOA'
		cur = conn.cursor()
		if asn1 == 0 and asn2 == 0:
			cur.execute('select PAIR_ID, \
					IPSV%d_1.AUTNUM as ASN1, name1.name as name1, %s(IP1) as IP1, \
					IPSV%d_2.AUTNUM as ASN2, name2.name as name2, %s(IP2) as IP2 \
					  from IPV%dPAIRS \
					    left join IPSV%d IPSV%d_1 on IPSV%d_1.IP = IPV%dPAIRS.IP1 \
					    left join asn_to_name as name1 on IPSV%d_1.AUTNUM = name1.asn \
					    left join IPSV%d IPSV%d_2 on IPSV%d_2.IP = IPV%dPAIRS.IP2 \
					    left join asn_to_name as name2 on IPSV%d_2.AUTNUM = name2.asn \
						order by ASN1, ASN2' % (
							af, inet_ntoa,
							af, inet_ntoa,
							af,
							af, af, af, af,
							af,
							af, af, af, af,
							af))
		elif asn1 and asn2:
			cur.execute('select PAIR_ID, \
					IPSV%d_1.AUTNUM as ASN1, name1.name as name1, %s(IP1) as IP1, \
					IPSV%d_2.AUTNUM as ASN2, name2.name as name2, %s(IP2) as IP2 \
					  from IPV%dPAIRS \
					    left join IPSV%d IPSV%d_1 on IPSV%d_1.IP = IPV%dPAIRS.IP1 \
					    left join asn_to_name as name1 on IPSV%d_1.AUTNUM = name1.asn \
					    left join IPSV%d IPSV%d_2 on IPSV%d_2.IP = IPV%dPAIRS.IP2 \
					    left join asn_to_name as name2 on IPSV%d_2.AUTNUM = name2.asn \
						where ( IPSV%d_1.AUTNUM = %d and IPSV%d_2.AUTNUM = %d ) or ( IPSV%d_1.AUTNUM = %d and IPSV%d_2.AUTNUM = %d ) \
						order by ASN1, ASN2' % (
							af, inet_ntoa,
							af, inet_ntoa,
							af,
							af, af, af, af,
							af,
							af, af, af, af,
							af,
							af, asn1, af, asn2, af, asn2, af, asn1))
		else:
			if asn1:
				asn = asn1
			else:
				asn = asn2
			cur.execute('select PAIR_ID, \
					IPSV%d_1.AUTNUM as ASN1, name1.name as name1, %s(IP1) as IP1, \
					IPSV%d_2.AUTNUM as ASN2, name2.name as name2, %s(IP2) as IP2 \
					  from IPV%dPAIRS \
					    left join IPSV%d IPSV%d_1 on IPSV%d_1.IP = IPV%dPAIRS.IP1 \
					    left join asn_to_name as name1 on IPSV%d_1.AUTNUM = name1.asn \
					    left join IPSV%d IPSV%d_2 on IPSV%d_2.IP = IPV%dPAIRS.IP2 \
					    left join asn_to_name as name2 on IPSV%d_2.AUTNUM = name2.asn \
						where IPSV%d_1.AUTNUM = %d or IPSV%d_2.AUTNUM = %d \
						order by ASN1, ASN2' % (
							af, inet_ntoa,
							af, inet_ntoa,
							af,
							af, af, af, af,
							af,
							af, af, af, af,
							af,
							af, asn, af, asn))

		results = cur.fetchall()
		for r in results:
			pair_id = r[0]
			asn1 = r[1]
			name1 = r[2]
			ip1 = r[3]
			asn2 = r[4]
			name2 = r[5]
			ip2 = r[6]

			if name1 == None:
				asns_unknown[asn1] = asn1
			if asn1 != None:
				asns[asn1] = asn1
			if name2 == None:
				asns_unknown[asn2] = asn2
			if asn2 != None:
				asns[asn2] = asn2

			pairs.append({'pair_id':pair_id, 'af': af, 'asn1':asn1, 'name1':name1, 'ip1':ip1, 'asn2':asn2, 'name2':name2, 'ip2':ip2 })

		cur.close()

	if verbose:
		sys.stderr.write('dump_ippair: %d pairs found\n' % (len(results)))
		sys.stderr.write('dump_ippair: %d asns found\n' % (len(asns)))
		for k, v in sorted(asns_unknown.items()):
			sys.stderr.write('dump_ippair: %s UNKNOWN\n' % ('AS' + str(k)))

	return pairs

def pair_id_2_msm_ids(conn, pair_id):
	msm_ids = []

	cur = conn.cursor()
	cur.execute('select MIDS.`msm_id`, UNIX_TIMESTAMP(timestamp), description from MIDS left join measurements on MIDS.`msm_id` = measurements.`msm_id` where `pair_id` = %d limit 10' % (pair_id))
	results = cur.fetchall()
	for r in results:
		msm_id = int(r[0])
		timestamp = r[1]
		description = r[2]
		msm_ids.append({'msm_id': msm_id, 'timestamp': timestamp, 'description': description})
	cur.close()

	return msm_ids

def doit(conn, af_list, asn1, asn2, geo_file, results_file):

	ip_geo = collect_geo(conn, af_list);
	pairs = asntryst_get_ip_pairs(conn, af_list, asn1, asn2)

	asntryst = {}
	asntryst['type'] = 'FeatureCollection'
	asntryst['features'] = []

	for pair in pairs:
		pair_id = pair['pair_id']
		af = pair['af']
		asn1 = pair['asn1']
		name1 = pair['name1']
		ip1 = pair['ip1']
		asn2 = pair['asn2']
		name2 = pair['name2']
		ip2 = pair['ip2']

		as1 = ''
		if asn1 != None and asn1 != 0:
			if name1 == None or name1 == '':
				name1 = 'UNKNOWN'
			as1 = 'AS' + str(asn1) + '/' + name1

		as2 = ''
		if asn2 != None and asn2 != 0:
			if name2 == None or name1 == '':
				name2 = 'UNKNOWN'
			as2 = 'AS' + str(asn2) + '/' + name2

		latlon1 = ''
		place1 = None
		hostname1 = None
		if ip1 in ip_geo:
			latlon1 = '%10.5f,%10.5f' % (ip_geo[ip1]['lat'], ip_geo[ip1]['lon'])
			place1 = ip_geo[ip1]['place']
			hostname1 = ip_geo[ip1]['hostname']
		latlon2 = ''
		place2 = None
		hostname2 = None
		if ip2 in ip_geo:
			latlon2 = '%10.5f,%10.5f' % (ip_geo[ip2]['lat'], ip_geo[ip2]['lon'])
			place2 = ip_geo[ip2]['place']
			hostname2 = ip_geo[ip2]['hostname']

		if latlon1 != '' and latlon2 != '' and latlon1 == latlon2:
			coincident = True
			same_s = '=='
		else:
			coincident = False
			same_s = ''

		if coincident:
			## which one should I use? - write some code - if they are the same; then yippee
			# they are the same geo point
			pass

		if (asn1 < asn2):
			print('%-40s -> %-40s v%1d %28s -> %-28s ; %24s %2s %24s' % (as1[0:40], as2[0:40], af, ip1, ip2, latlon1, same_s, latlon2) )
		else:
			print('%-40s -> %-40s v%1d %28s -> %-28s ; %24s %2s %24s' % (as2[0:40], as1[0:40], af, ip2, ip1, latlon2, same_s, latlon1) )

		if latlon1 == '' and latlon2 == '':
			## No Geo for any point in this pair - make sure we say which measurement this is - so we can add geo later
			msm_ids = pair_id_2_msm_ids(conn, pair_id)
			for m in msm_ids:
				msm_id = m['msm_id']
				timestamp = m['timestamp']
				description = m['description']
				print ('+++ check https://marmot.ripe.net/openipmap/tracemap?msm_ids=%d&show_suggestions=0&max_probes=50 ; %s ; %s' %(msm_id, timestamp, description))

		if ip1 in ip_geo:
			c1 = [ip_geo[ip1]['lon'], ip_geo[ip1]['lat']]
			if ip2 in ip_geo:
				c2 = [ip_geo[ip2]['lon'], ip_geo[ip2]['lat']]
			else:
				c2 = None
			if (asn1 < asn2):
				p = {'af': af, 'ip1': ip1, 'as1': as1, 'ip2': ip2, 'as2': as2, 'place1': place1, 'hostname1': hostname1, 'place2': place2, 'hostname2': hostname2, 'coincident': coincident, 'c2': c2}
				f = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c1}, 'properties': p}
			else:
				p = {'af': af, 'ip2': ip2, 'as2': as2, 'ip1': ip1, 'as1': as1, 'place1': place2, 'hostname1': hostname2, 'place2': place1, 'hostname2': hostname1, 'coincident': coincident, 'c2': c2}
				f = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c1}, 'properties': p}
			asntryst['features'].append(f)

		# don't worry about second IP geo location if it's the same as the first one
		if ip2 in ip_geo and not coincident:
			c1 = [ip_geo[ip2]['lon'], ip_geo[ip2]['lat']]
			if ip1 in ip_geo:
				c2 = [ip_geo[ip1]['lon'], ip_geo[ip1]['lat']]
			else:
				c2 = None
			if (asn1 < asn2):
				p = {'af': af, 'ip1': ip1, 'as1': as1, 'ip2': ip2, 'as2': as2, 'place1': place1, 'hostname1': hostname1, 'place2': place2, 'hostname2': hostname2, 'coincident': coincident, 'c2': c2}
				f = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c1}, 'properties': p}
			else:
				p = {'af': af, 'ip2': ip2, 'as2': as2, 'ip1': ip1, 'as1': as1, 'place1': place2, 'hostname1': hostname2, 'place2': place1, 'hostname2': hostname1, 'coincident': coincident, 'c2': c2}
				f = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': c1}, 'properties': p}
			asntryst['features'].append(f)

	if results_file:
		with open(results_file, 'w') as fd:
			fd.write('var asntryst =\n')
			fd.write(json.dumps(asntryst))
			fd.write('\n;\n')

	if geo_file:
		with open(geo_file, 'w') as fd:
			fd.write(json.dumps(ip_geo))

def main(argv):
	global verbose
	asn1 = 0
	asn2 = 0
	geo_file = None
	results_file = None
	af_list = [4, 6]

	help_string = 'usage: asntryst-dump.py [--help] [--verbose] [--as1 ASN1] [--as2 ASN2] [--geo file] [--results file]\n'

	try:
		opts, args = getopt.getopt(argv, 'hv46a:b:g:r:', ['help', 'verbose', '4', '6', 'as1=', 'as2=', 'geo=*', 'results=*'])
	except getopt.GetoptError:
		sys.stderr.write(help_string)
		sys.exit(1)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			sys.stderr.write(help_string)
			sys.exit(0)
		elif opt in ('-v', '--verbose'):
			verbose = 1
		elif opt in ('-4', '--4'):
			af_list = [4]
		elif opt in ('-6', '--6'):
			af_list = [6]
		elif opt in ('-a', '--as1'):
			asn1 = arg
		elif opt in ('-b', '--as2'):
			asn2 = arg
		elif opt in ('-g', '--geo'):
			geo_file = arg
		elif opt in ('-r', '--results'):
			results_file = arg

	if len(args) > 0:
		sys.stderr.write(help_string)
		sys.exit(1)

	c = asntryst_read_config()
	d = c['database']

	conn = MySQLdb.connect(host=d['hostname'], user=d['username'], passwd=d['password'], db=d['database'])
	doit(conn, af_list, int(asn1), int(asn2), geo_file, results_file)
	conn.close()

if __name__ == '__main__':
   main(sys.argv[1:])

sys.exit(0)

