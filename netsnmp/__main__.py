import netsnmp._api as netsnmp

[print(k, '=', v) for k, v in sorted(netsnmp.__dict__.items())]
