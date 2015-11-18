#!/usr/bin/env python

import ConfigParser

CONFIG_FILE = '../private/config.cfg'

def asntryst_read_config():
	config = ConfigParser.RawConfigParser()
	config.read(CONFIG_FILE)
	r = {}
	## database
	r['database'] = {}
	r['database']['database'] = config.get('database', 'database')
	r['database']['hostname'] = config.get('database', 'hostname')
	r['database']['username'] = config.get('database', 'username')
	r['database']['password'] = config.get('database', 'password')
	## add more here when needed
	return r

