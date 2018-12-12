#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#

from .abc import GrumpyBasePlugin


class GrumpyPlugin(GrumpyBasePlugin):

    counter = {}

    def __init__(self, connection):
        super().__init__(connection)

    def run(self, sender, destination, message):
        print('running counter plugin')
