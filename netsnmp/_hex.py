import binascii, struct

def snmp_hex2str(type, value):
    """
    Helper func to convert various types of hex-strings, determined by length
    """

    # if not "Hex" in type, return unaltered below
    if "Hex" in type:
        # Remove any quotes
        _hexstr = value.replace('"', '')
    
        if len(_hexstr)==18:
            # Return cleanly formatted MAC address, no conversion nescessary
            type = "MacAddress"
            value = '%s:%s:%s:%s:%s:%s' % tuple(_hexstr.split())
    
        elif len(_hexstr)==12:
            ## Convert octal IpAddress
            # example input: C0 A8 01 01
            # C0 = 192
            # A8 = 168
            # 01 = 1
            # 01 = 1
            type = "IpAddress"
            value = '%d.%d.%d.%d' % tuple([ord(binascii.unhexlify(part)) for part in _hexstr.split()])

        elif len(_hexstr)==33:
            ## Convert DateAndTime
            # example input: 07 DF 0C 0E 16 15 09 00 2D 05 00
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
            utcdir, utchour, utcminute) = [ord(binascii.unhexlify(part)) for part in _hexstr.split()[2:]]

            value = '%d-%d-%d,%0#2d:%0#2d:%0#2d.%d,%s%s:%s' % (
                    year, month, day, hour, minute, second, decisecond, chr(utcdir), utchour, utcminute)

    return (type, value)