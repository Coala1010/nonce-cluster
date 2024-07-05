def get_b03(nonce):
    x = int(nonce, 16)
    b0 = x >> 25
    b3 = x >> 1 & 0x7F 
    return b0, b3

def get_b12(nonce):
    x = int(nonce, 16)
    b1 = x >> 17 & 0x7F 
    b2 = x >> 9 & 0x7F 
    return b1, b2