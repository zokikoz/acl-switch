#!/usr/bin/env python3
# Cisco ACL switch

import telnetlib
import getpass
import re

# Default configuration
params = {
    'ip': '', 'username': '', 'password': '', 'enable': '',
    'direction': 'Inbound', 'acl1': 'not set', 'acl2': 'not set', 'interface': 'gi0/0'
    }

def to_bytes(string):
    return f"{string}\n".encode('utf-8')

def login(telnet):
    # Accessing to device
    if params['username']:
        telnet.read_until(b'Username')
        telnet.write(to_bytes(params['username']))
    telnet.read_until(b'Password')
    telnet.write(to_bytes(params['password']))
    # Checking enable status
    index, *_ = telnet.expect([b'>', b'#'])
    # Switching to privilege mode using enable password
    if index == 0 and params['enable'] != False:
        telnet.write(b'enable\n')
        telnet.read_until(b'Password')
        telnet.write(to_bytes(params['enable']))
        telnet.read_until(b'#', timeout=5)

def execute(telnet, commands):
    # Running commands
    result = {}
    for command in commands:
        telnet.write(to_bytes(command))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8')
        result[command] = output.replace('\r\n', '\n')
    return result

def set_acl_cmd(output, direction = params['direction']):
    # Setting new ACL different from current
    if output['ACL'] == params['acl1']:
        acl = params['acl2']
    elif output['ACL'] == params['acl2']:
        acl = params['acl1']
    else:
        return False
    # Setting direction for ACL command
    for long, short in {'Inbound':'in', 'Outgoing':'out'}.items():
        direction = direction.replace(long, short)
    # Completing ACL command
    if acl == 'not set': 
        acl = f'no ip access group {direction}'
    else: 
        acl = f'ip access {acl} {direction}'
    # Setting full commands list
    return ['conf t', f"int {params['interface']}", acl]

def acl_change():
    with telnetlib.Telnet(params['ip']) as telnet:
        login(telnet)
        # Getting interface ACL
        telnet.write(to_bytes(f"sh ip int {params['interface']} | include {params['direction']}"))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8').replace('\r\n', '\n')
        output = re.search(r'access list is (?P<ACL>.+)\n', output)
        # Preparing commands list
        commands = set_acl_cmd(output)
        return execute(telnet, commands)
        
if not params['ip']: params['ip'] = input('IP: ')
if not params['username']: params['username'] = input('Username: ')
if not params['password']: params['password'] = getpass.getpass()
if not params['enable'] and params['enable'] != False: params['enable'] = getpass.getpass('Enable: ')

result = acl_change()
print(result)
