#
# Author: Frantisek Kolacek
# Version: 1.0
#

from abc import ABC


class GrumpyBasePlugin(ABC):

    def __init__(self, config, connection):
        self.config = config
        self.connection = connection

    def run(self, sender, destination, message):
        raise NotImplementedError('')
