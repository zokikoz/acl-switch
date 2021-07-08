#!/usr/bin/env python3
# Cisco ACL changer

import telnetlib
import getpass
import re

params = {
    'ip': '', 'username': '', 'password': '', 'enable': '',
    'direction': 'Inbound', 'acl1': 'not set', 'acl2': 'not set', 'interface': 'gi0/0'
    }

if not params['ip']: params['ip'] = input('IP: ')
if not params['username']: params['username'] = input('Username: ')
if not params['password']: params['password'] = getpass.getpass()
if not params['enable'] and params['enable'] != False: params['enable'] = getpass.getpass('Enable: ')

def to_bytes(string):
    return f"{string}\n".encode('utf-8')

def privelege_mode(telnet):
    # Switching to privelege mode by enable password
    if params['enable'] == False: return

    telnet.write(b'enable\n')
    telnet.read_until(b'Password')
    telnet.write(to_bytes(params['enable']))
    telnet.read_until(b'#', timeout=5)

def set_acl_cmd(device, direction = params['direction']):
    # Setting new ACL different from current
    if device['ACL'] == params['acl1']:
        acl = params['acl2']
    elif device['ACL'] == params['acl2']:
        acl = params['acl1']
    else:
        return False
    # Setting direction for ACL command
    for long, short in {'Inbound':'in', 'Outgoing':'out'}.items():
        direction = direction.replace(long, short)
    # Completing command
    if acl == 'not set': 
        acl_command = f'no ip access group {direction}'
    else: 
        acl_command = f'ip access {direction} {acl}'
    return acl_command

def set_commands(acl):
    if not acl: return False
    
    return ['conf t', f"int {params['interface']}", acl]


def acl_change():
    with telnetlib.Telnet(params['ip']) as telnet:
        if params['username']:
            telnet.read_until(b'Username')
            telnet.write(to_bytes(params['username']))
        telnet.read_until(b'Password')
        telnet.write(to_bytes(params['password']))
        index, *_ = telnet.expect([b'>', b'#'])
        # Checking enable status
        if index == 0: privelege_mode(telnet)
        # Getting interface ACL
        telnet.write(to_bytes(f"sh ip int {params['interface']} | include {params['direction']}"))
        output = telnet.read_until(b'#', timeout=5).decode('utf-8').replace('\r\n', '\n')
        device = re.search(r'access list is (?P<ACL>.+)\n', output)
        # Setting ACL command
        acl = set_acl_cmd(device)
        # Setting complete commands
        result = set_commands(acl)

        return result

result = acl_change()
print(result)
