#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#

import logging
import socket
import re
from importlib import import_module

from .exception import GrumpyException, GrumpyRuntimeException
from .config import GrumpyConfig


class Grumpy:

    config = None
    plugins = {}
    connection = None

    def __init__(self, config_name='config.ini'):
        try:
            self.config = GrumpyConfig(config_name)

            self.init_logging()
            self.init_plugins()

        except GrumpyException:
            raise

    def init_logging(self):
        level = logging.DEBUG if self.config['main']['debug'] else logging.INFO

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=level)

    def init_plugins(self):
        logging.info('Loading plugins')
        for name in self.config['main']['plugins']:
            try:
                logging.info('Loading plugin: {}'.format(name))
                module = import_module('grumpy.plugins.{}'.format(name))
                plugin = getattr(module, 'GrumpyPlugin')

                self.plugins[name] = plugin(self.config, self.connection)
            except ImportError:
                raise GrumpyRuntimeException('Cannot load plugin: {}'.format(name)) from None

    def run(self):
        logging.info('Starting bot')

        conf = self.config['main']

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info('Connecting to: {}:{}'.format(conf['server'], conf['port']))
        self.connection.connect((conf['server'], conf['port']))

        user = 'USER {} {} {}: {}'.format(conf['nick'],
                                          conf['hostname'],
                                          conf['servername'],
                                          conf['realname'])
        nick = 'NICK {}'.format(conf['nick'])

        self._send_raw_message(user)
        self._send_raw_message(nick)

        buffer = ''
        while True:
            buffer += self.connection.recv(1024).decode()

            buffer = self._handle_response(buffer)

    def _send_raw_message(self, message):
        logging.info('======> "{}"'.format(message))

        self.connection.send('{}\n'.format(message).encode())

    def _send_message(self, dest, message):
        output = 'PRIVMSG {} :{}'.format(dest, message)

        self._send_raw_message(output)

    def _handle_response(self, buffer):
        conf = self.config['main']
        uconf = self.config['userserv']

        lines = buffer.splitlines(keepends=True)

        for line in lines:
            # We process just complete lines
            if not line.endswith('\n'):
                return line

            line = line.strip()

            if line == '':
                continue


            # NOTICE messages
            if re.match('^NOTICE AUTH', line):
                logging.info('<====== "{}"'.format(line))
            # Initialization is done
            elif re.search('^:{} 376 {} :End of /MOTD command.'.format(conf['server'], conf['nick']), line):
                logging.info('<====== "{}"'.format(line))

                # if userserv is defined
                if all([uconf['username'], uconf['password']]):
                    self._send_message('userserv', 'login {} {}'.format(uconf['username'], uconf['password']))

                # regain nick using nickserv
                if uconf['nickserv']:
                    self._send_message('nickserv', 'REGAIN {}'.format(conf['nick']))

                # join all channels
                for channel in conf['channels']:
                    self._send_message('chanserv', 'INVITE {}'.format(channel))
                    self._send_raw_message('JOIN {}'.format(channel))
            # INVITES from chanserv
            elif re.match('^:CHANSERV!chan@services.int INVITE', line):
                logging.info('<====== "{}"'.format(line))

                m = re.match('^:CHANSERV!chan@services.int INVITE .+:(.+)$', line)

                if not m:
                    continue

                self._send_raw_message('JOIN {}'.format(m.group(1)))
            # Status messages
            elif re.match('^:{} [0-9]+ {} '.format(conf['server'], conf['nick']), line):
                logging.info('<====== "{}"'.format(line))
            # PING messages
            elif re.match('^PING :', line):
                logging.info('<====== "{}"'.format(line))

                self._send_raw_message('PONG :{}'.format(conf['server']))
            # PRIVMSG
            elif re.match('^:.+ PRIVMSG .+ :', line):
                logging.info('<====== "{}"'.format(line))

                m = re.match('^:(.+)!~.+ PRIVMSG (.+) :(.+)$'.format(conf['nick']), line)

                if not m:
                    continue

                self._handle_message(m.group(1), m.group(2), m.group(3))
            # Unhandled messages
            else:
                logging.warning('<=== "{}"'.format(line))

        # In case all lines were processed empty the buffer
        return ''

    def _handle_message(self, sender, destination, message):
        for name, plugin in self.plugins.items():
            try:
                logging.debug('{} | {} | {} | {}'.format(name, sender, destination, message))
                messages = plugin.run(sender, destination, message)

                for message in messages:
                    self._send_message(message['destination'], message['message'])
            except GrumpyRuntimeException as e:
                logging.error(e)




