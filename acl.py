#!/usr/bin/env python3
# Cisco ACL changer

import telnetlib
import getpass
import re

params = {
    'ip': '', 'username': '', 'password': '', 'enable': '',
    'direction': 'Inbound', 'acl1': '', 'acl2': '', 'interface': 'gi0/0'
    }

if not params['ip']: params['ip'] = input('IP: ')
if not params['username']: params['username'] = input('Username: ')
if not params['password']: params['password'] = getpass.getpass()
if not params['enable'] and params['enable'] != False: params['enable'] = getpass.getpass('Enable: ')

def to_bytes(string):
    return f"{string}\n".encode('utf-8')

def privelege_mode(telnet, enable):
    telnet.write(b'enable\n')
    telnet.read_until(b'Password')
    telnet.write(to_bytes(enable))
    telnet.read_until(b'#', timeout=5)

def acl_change(ip, username, password, enable, direction, acl1, acl2, interface):
    with telnetlib.Telnet(ip) as telnet:
        if params['username']:
            telnet.read_until(b'Username')
            telnet.write(to_bytes(username))
        telnet.read_until(b'Password')
        telnet.write(to_bytes(password))
        index, *_ = telnet.expect([b'>', b'#'])
        # Check enable status
        if index == 0 and enable != False: privelege_mode(telnet, enable)
        # Get interface ACL
        telnet.write(to_bytes(f"sh ip int {interface} | include {direction}"))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8').replace('\r\n', '\n')
        result = re.search(r'access list is (?P<ACL>.+)\n', output)
        return result

result = acl_change(**params)
print(result['ACL'])
