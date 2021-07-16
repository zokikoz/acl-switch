#!/usr/bin/env python3
# Cisco ACL switch

import ciscotn
import getpass
import re
import yaml
import sys


class CiscoTelnet(ciscotn.CiscoTelnet):
    """ACL methods mixin to CiscoTelnet class"""
    
    def __init__(self, direction='Inbound', acl1=None, acl2=None, interface=None, **kwargs):
        self.direction = direction
        self.acl1 = acl1
        self.acl2 = acl2
        self.interface = interface
        super().__init__(**kwargs)

    def get_acl(self):
        """Getting current ACL on interface"""
        cmd = f'sh ip int {self.interface} | include {self.direction}'
        output = self.execute([cmd])
        output = re.search(r'access list is (?P<ACL>.+)\n', output[cmd])
        if output:
            print(f"{self.interface} {self.direction}: {output['ACL']}")
            return output
        else: 
            raise ConnectionError('Unable to access device')

    def set_acl_cmd(self, interface):
        """Preparing command list for ACL switch"""
        # Setting new ACL different from current
        if interface['ACL'] == self.acl1:
            acl = self.acl2
        elif interface['ACL'] == self.acl2:
            acl = self.acl1
        else:
            raise ConnectionError('Unable to find selected ACLs on interface')
        print(f"Switching ACL: {interface['ACL']} -> {acl}")
        # Setting direction for ACL command
        direction = self.direction
        for full, short in {'Inbound':'in', 'Outgoing':'out'}.items():
            direction = direction.replace(full, short)
        # Completing ACL command
        acl = f'no ip access {direction}' if acl == 'not set' else f'ip access {acl} {direction}'
        # Setting full commands list
        return ['conf t', f'int {self.interface}', acl, 'exit', 'exit']


def input_check(param):
    if not param['ip']:
        param['ip'] = input('IP: ')
    if not param['username'] and param['username'] is not False:
        param['username'] = input('Username: ')
    if not param['password']:
        param['password'] = getpass.getpass()
    if not param['enable'] and param['enable'] is not False:
        param['enable'] = getpass.getpass('Enable: ')
    if not param['acl1']:
        param['acl1'] = input('ACL 1: ')
    if not param['acl2']:
        param['acl2'] = input('ACL 2: ')
    if not param['interface']:
        param['interface'] = input('Interface: ')
    return param


def acl_switch(param):
    """Switches ACL on Cisco device"""
    with CiscoTelnet(**param) as cisco:
        cisco.login()
        interface = cisco.get_acl()
        commands = cisco.set_acl_cmd(interface)
        cisco.execute(commands)
        cisco.get_acl()

try:
    with open('config.yaml') as f:
        params = yaml.safe_load(f)
except FileNotFoundError:
   print('config.yaml not found, using built-in configuration')
   params = [{}]

sys.tracebacklimit = 0  # Hide traceback
if sys.argv[1:] and sys.argv[1] == '-v':
    sys.tracebacklimit = 1000  # Enable traceback
    for param in params: param['verbose'] = True

for param in params:
    param = input_check(param)
    acl_switch(param)
