#!/usr/bin/python

######################################################################
#
# lbsc.py - location based service configurator
#
# (c) 2013 Alexander Stellwag <thorwin@thorwinsworld.de>
#
# This script matches the current ip configuration against the array
# locations and if a matching entry is found, configures a list of
# defined services by symlinking their config fdiles and restarting
# the services
#
# Configuration is done in /etc/lbsc.conf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import configparser
import os
import re
import subprocess

locations={}
services={}

def ip_address( iface ):
	p = subprocess.Popen( ["ip","addr","show",iface], stdout=subprocess.PIPE)
	lines = p.stdout.readlines()
	p.wait

	for l in lines:
		adr = re.match( b'\s+inet ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', l)
		if adr:
			return adr.group(1).decode('utf-8')

def get_interfaces():
	interfaces = {}
	p = subprocess.Popen( ["ip","link","show"], stdout=subprocess.PIPE)
	lines = p.stdout.readlines()
	p.wait()

	for l in lines:
		iface = re.match( b'^\w+:\s+(\w+):.*<.*,UP,.*>.*', l)
		if iface:
			i = iface.group(1).decode('utf-8')
			interfaces[i] = ip_address(i)

	return interfaces

def get_config( file ):
	config = configparser.RawConfigParser()
	config.read('lbsc.conf')
	for s in str.split(config.get('default', 'services')):
		services[s] = {}
		services[s]['file'] = config.get('service-'+s, 'file')

	for l in str.split(config.get('default', 'locations')):
		locations[l] = {}
		locations[l]['interface'] = config.get('location-'+l, 'interface')
		locations[l]['regex'] = config.get('location-'+l, 'regex')

	

get_config( 'lbsc.conf' )

interfaces = get_interfaces()

for l in locations:
	if locations[l]['interface'] in interfaces and re.match( locations[l]['regex'], interfaces[locations[l]['interface']] ):
		print(l)
