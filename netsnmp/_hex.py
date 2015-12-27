import binascii, struct

def snmp_hex2str(type, value):
    """
    Helper func to convert various types of hex-strings, determined by length
    """

    # Remove any surrounding quotes
    if value[0]=='"' and value[-1]=='"':
        # '"AB'" -> 'AB'
        _hexstr = value[1:-1]
    else:
        _hexstr = value

    _hexstrl = len(_hexstr)

    if _hexstrl==18:
        # Return cleanly formatted MAC address, no conversion nescessary
        type = "MacAddress"
        value = '%s:%s:%s:%s:%s:%s' % tuple(_hexstr.split())

    elif _hexstrl==12 or _hexstrl==4:
        ## Convert octal IpAddress
        # example input: 'C0 A8 01 01 ' or 'DV8W'
        # C0 = 192
        # A8 = 168
        # 01 = 1
        # 01 = 1
        type = "IpAddress"
        if _hexstrl==4:
            # Convert ascii-alike strings
            value = '%d.%d.%d.%d' % tuple((ord(char) for char in _hexstr))
        else:
            # Convert hex strings
            value = '%d.%d.%d.%d' % tuple((ord(binascii.unhexlify(part)) for part in _hexstr.split()))

    elif _hexstrl==33:
        ## Convert DateAndTime
        # example input: '07 DF 0C 0E 16 15 09 00 2D 05 00 '
        # 07 DF = year
        # 0C = month
        # 0E = day
        # 16 = hour
        # 15 = minutes
        # 09 = seconds
        # 00 = deci-seconds
        # 2D = direction from UTC ('+'/'-'), e.g. chr(45)==str('-')
        # 05 = hours from UTC
        # 00 = minutes from UTC
        type = "DateAndTime"

        # given above example, unhexlify "07DF" (b'\x07\xdf') then unpack as big-endian unsigned short (2015)
        year = struct.unpack('>H', binascii.unhexlify("".join(_hexstr.split()[:2])))[0]

        (month, day, hour, minute, second, decisecond,
        utcdir, utchour, utcminute) = (ord(binascii.unhexlify(part)) for part in _hexstr.split()[2:])

        # zero padded hour, minute, second
        value = '%d-%d-%d,%0#2d:%0#2d:%0#2d.%d,%s%s:%s' % (
                year, month, day, hour, minute, second, decisecond, chr(utcdir), utchour, utcminute)

    return (type, value)
