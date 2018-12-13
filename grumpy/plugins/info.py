#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

from .abc import GrumpyBasePlugin


class GrumpyPlugin(GrumpyBasePlugin):

    def __init__(self, config, connection):
        super().__init__(config, connection)

    def run(self, sender, destination, message):
        print('Running info plugin')

        return []
