CHECKSUM_MOD = 1 << 16

def _chunk_bytes(mbytes, length):
    """ creates fixed-size chunks of segment contents for checksum calculation """
    return (mbytes[0+i:length+i] for i in range(0, len(mbytes), length))

def _bin_add(b1, b2):
    """ 1's compl addition of binary ints """
    return b1+b2 if CHECKSUM_MOD > b1 + \
        b2 else (b1+b2+1) % CHECKSUM_MOD

def checksum(header, data):
    """ Calculates 16 bit UDP checksum of byte data
    
    Args:
        header (Header): header obj
        data (byte): data in byte string
    
    Returns:
        bytes: byte string repr of calculated checksum
    """
    checksum = 0b0000000000000000
    header_bytes = header.seq + header.stype
    for chunk in _chunk_bytes(header_bytes+data, 16):
        checksum = _bin_add(checksum, int(chunk,2))
    return '{0:016b}'.format(checksum).encode()