#!/usr/bin/env python3
# Cisco ACL switch

import telnetlib
import getpass
import re
import yaml

# Default configuration
params = [{
    'ip': None, 'username': None, 'password': None, 'enable': None,
    'direction': 'Inbound', 'acl1': None, 'acl2': None, 'interface': None
    }]

try:
    with open('config.yaml') as f:
        params = yaml.safe_load(f)
except FileNotFoundError:
   print('config.yaml not found, using built-in configuration')

def to_bytes(string):
    return f"{string}\n".encode('utf-8')

def input_check(param):
    if not param['ip']: param['ip'] = input('IP: ')
    if not param['username']: param['username'] = input('Username: ')
    if not param['password']: param['password'] = getpass.getpass()
    if not param['enable'] and param['enable'] != False: param['enable'] = getpass.getpass('Enable: ')
    if not param['acl1']: param['acl1'] = input('ACL 1: ')
    if not param['acl2']: param['acl2'] = input('ACL 2: ')
    if not param['interface']: param['interface'] = input('Interface: ')
    return param

def login(telnet, param):
    # Accessing to device
    if param['username']:
        telnet.read_until(b'Username')
        telnet.write(to_bytes(param['username']))
    telnet.read_until(b'Password')
    telnet.write(to_bytes(param['password']))
    # Checking enable status
    index, *_ = telnet.expect([b'>', b'#'])
    # Switching to privilege mode using enable password
    if index == 0 and param['enable'] != False:
        telnet.write(b'enable\n')
        telnet.read_until(b'Password')
        telnet.write(to_bytes(param['enable']))
        telnet.read_until(b'#', timeout=5)

def execute(telnet, commands):
    # Running commands
    result = {}
    for command in commands:
        telnet.write(to_bytes(command))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8')
        result[command] = output.replace('\r\n', '\n')
    return result

def set_commands(output, param):
    # Setting new ACL different from current
    if output['ACL'] == param['acl1']:
        acl = param['acl2']
    elif output['ACL'] == param['acl2']:
        acl = param['acl1']
    else:
        print('Unable to find selected ACLs on interface')
        return False
    print(f"Switching ACL: {output['ACL']} -> {acl}")
    # Setting direction for ACL command
    direction = param['direction']
    for full, short in {'Inbound':'in', 'Outgoing':'out'}.items():
        direction = direction.replace(full, short)
    # Completing ACL command
    acl = f'no ip access {direction}' if acl == 'not set' else f'ip access {acl} {direction}'
    # Setting full commands list
    return ['conf t', f"int {param['interface']}", acl]

def acl_change(param):
    with telnetlib.Telnet(param['ip']) as telnet:
        login(telnet, param)
        # Getting interface ACL
        telnet.write(to_bytes(f"sh ip int {param['interface']} | include {param['direction']}"))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8').replace('\r\n', '\n')
        output = re.search(r'access list is (?P<ACL>.+)\n', output)
        # Preparing commands list
        commands = set_commands(output, param)
        return execute(telnet, commands)

for param in params:
    param = input_check(param)
    result = acl_change(param)
    print(result)
