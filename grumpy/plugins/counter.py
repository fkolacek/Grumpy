#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

import re

from .abc import GrumpyBasePlugin


class GrumpyPlugin(GrumpyBasePlugin):

    counter = {}

    def __init__(self, connection):
        super().__init__(connection)

    def run(self, sender, destination, message):
        m = re.search('^([^+\-]+)(\+\+|\-\-) ?$',message)

        if not m:
            return []

        target = m.group(1)
        operation = 1 if m.group(2) == '++' else -1

        if target not in self.counter:
            self.counter[target] = 0

        self.counter[target] = self.counter[target] + operation

        message = 'Counter for "{}" has been updated to: {}'.format(target, self.counter[target])

        return [{'destination': sender, 'message': message}]
