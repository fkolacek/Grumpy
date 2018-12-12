#
# Author: Frantisek Kolacek <work@kolacek.it
# Version: 1.0
#


class GrumpyException(Exception):
    pass


class GrumpyConfigException(GrumpyException):
    pass


class GrumpyRuntimeException(GrumpyException):
    pass
