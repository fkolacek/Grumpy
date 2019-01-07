#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

import os.path
import re
import json

from .abc import GrumpyBasePlugin


class GrumpyPlugin(GrumpyBasePlugin):

    counter = {}

    def __init__(self, config, connection):
        super().__init__(config, connection)

        self._load_counter()

    def run(self, sender, destination, message):
        m = re.search('^([^+\-]+)(\+\+|\-\-) ?$', message)

        if not m:
            return []

        target = m.group(1)
        operation = 1 if m.group(2) == '++' else -1
        dest = sender if destination == self.config['main']['nick'] else destination

        if target not in self.counter:
            self.counter[target] = 0

        self.counter[target] = self.counter[target] + operation

        self._save_counter()

        message = 'Counter for "{}" has been updated to: {}'.format(target, self.counter[target])

        return [{'destination': dest, 'message': message}]

    def _load_counter(self):
        if os.path.exists('counter.data'):
            with open('counter.data') as f:
                self.counter = json.loads(f.read())

    def _save_counter(self):
        with open('counter.data', 'w') as f:
            f.write(json.dumps(self.counter))

