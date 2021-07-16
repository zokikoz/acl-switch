"""Cisco device Telnet client subclass"""

from telnetlib import Telnet


class CiscoTelnet(Telnet):
    """Cisco device access via telnet session"""
    
    def __init__(self, ip=None, username=None, password=None, enable=False, verbose=False, timeout=10):
        self.username = username
        self.password = password
        self.enable = enable
        self.verbose = verbose
        Telnet.__init__(self, ip, timeout=timeout)

    def login(self, timeout=3):
        """Cisco device login"""
        if self.username:
            self.read_until(b'Username', timeout)
            self.write(self.to_bytes(self.username))
        self.read_until(b'Password', timeout)
        self.write(self.to_bytes(self.password))
        # Checking enable status
        index, *_ = self.expect([b'>', b'#'], timeout)
        # Switching to privilege mode using enable password
        if index == -1:
            raise ConnectionError('Unable to login')
        elif index == 0 and self.enable:
            self.write(b'enable\n')
            self.read_until(b'Password', timeout)
            self.write(self.to_bytes(self.enable))
            index, *_ = self.expect([b'#'], timeout)
            if index == -1: raise ConnectionError('Unable to set privilege mode')

    def execute(self, commands, timeout=5):
        """Running command list"""
        result = {}
        for command in commands:
            self.write(self.to_bytes(command))
            output = self.read_until(b'#', timeout).decode('utf-8')
            result[command] = output.replace('\r\n', '\n')
        if self.verbose:
            for i in result.values(): print(i)
        return result

    @staticmethod
    def to_bytes(string):
        return f'{string}\n'.encode('utf-8')
