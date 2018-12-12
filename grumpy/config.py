#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#

import configparser

from .exception import  GrumpyConfigException


class GrumpyConfig:

    config = {
        'main': {
            'server': '',
            'port': 6667,
            'channels': [],
            'nick': 'Grumpy',
            'hostname': 'hostname',
            'servername': 'servername',
            'realname': 'Lord Grumpy',
            'debug': False,
        },
        'userserv': {
            'username': None,
            'password': None,
            'nickserv': False,
        },
    }

    def __init__(self, config_name):
        conf = configparser.ConfigParser()

        try:
            conf.read(config_name)
        except configparser.Error:
            raise GrumpyConfigException('Unable to parse config file: "{}"'.format(config_name)) from None

        for section in conf.sections():
            if section == 'main':
                self._parse_main(conf, section)
            elif section == 'userserv':
                self._parse_userserv(conf, section)
            else:
                raise GrumpyConfigException('Invalid section "{}" in config file: "{}"'.format(section, config_name))

    def _parse_main(self, conf, section):
        for key in conf[section]:
            if key == 'server':
                self.config[section][key] = conf[section][key]
            elif key == 'port':
                self.config[section][key] = int(conf[section][key])
            elif key == 'channels':
                self.config[section][key] = conf[section][key].split(',')
            elif key == 'nick':
                self.config[section][key] = conf[section][key]
            elif key == 'realname':
                self.config[section][key] = conf[section][key]
            elif key == 'hostname':
                self.config[section][key] = conf[section][key]
            elif key == 'servername':
                self.config[section][key] = conf[section][key]
            elif key == 'debug':
                self.config[section][key] = conf[section][key].lower() == 'true'
            else:
                raise GrumpyConfigException('Invalid key "{}" found "{}" section'.format(key, section))

    def _parse_userserv(self, conf, section):
        for key in conf[section]:
            if key == 'username':
                self.config[section][key] = conf[section][key]
            elif key == 'password':
                self.config[section][key] = conf[section][key]
            elif key == 'nickserv':
                self.config[section][key] = conf[section][key].lower() == 'true'
            else:
                raise GrumpyConfigException('Invalid key "{}" found "{}" section'.format(key, section))

    def __getitem__(self, item):
        return self.config.get(item)




