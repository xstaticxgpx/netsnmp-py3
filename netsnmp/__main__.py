# Python 2 support
from __future__ import print_function

import netsnmp._api

[print(k, '=', v) for k, v in sorted(netsnmp._api.__dict__.items())]
