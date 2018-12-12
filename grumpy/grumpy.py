#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#

import logging
import socket
import re

from .exception import GrumpyException
from .config import GrumpyConfig


class Grumpy:

    config = None
    connection = None

    def __init__(self, config_name='config.ini'):
        try:
            self.config = GrumpyConfig(config_name)

            self.init_logging()

        except GrumpyException:
            raise

    def init_logging(self):
        level = logging.DEBUG if self.config['main']['debug'] else logging.INFO

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=level)

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
                pass
            elif re.match('^NOTICE AUTH', line):
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
            elif re.match('^:CHANSERV!chan@services.int INVITE', line):
                m = re.match('^:CHANSERV!chan@services.int INVITE .+:(.+)$', line)

                if m:
                    self._send_raw_message('JOIN {}'.format(m.group(1)))

            elif re.match('^:{} [0-9]+ {} '.format(conf['server'], conf['nick']), line):
                logging.info('<====== "{}"'.format(line))
            elif re.match('^PING :', line):
                logging.info('<====== "{}"'.format(line))
                self._send_raw_message('PONG :{}'.format(conf['server']))
            else:
                print(line)

        # In case all lines were processed empty the buffer
        return ''


