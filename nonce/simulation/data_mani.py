import numpy as np
import numpy.testing as np_test

def get_byte0(nonce, endian='big'):
    if endian == 'big':
        # Extract the first byte (most significant byte) from the big-endian encoding
        first_byte = nonce >> 24
    elif endian == 'little':
        # Extract the first byte (least significant byte) from the little-endian encoding
        first_byte = nonce & 0xFF
    else:
        raise ValueError("Invalid endian specified. Use 'big' or 'little'.")

    return first_byte

def get_byte0_array(nonce_array, endian='big'):
    if endian == 'big':
        # Extract the first byte (most significant byte) from the big-endian encoding
        first_byte_array = nonce_array >> 24
    elif endian == 'little':
        # Extract the first byte (least significant byte) from the little-endian encoding
        first_byte_array = nonce_array & 0xFF
    else:
        raise ValueError("Invalid endian specified. Use 'big' or 'little'.")

    return first_byte_array

def extract_first_7_bits(nonce, endian='big'):
    if endian == 'big':
        # Extract the first 7 bits from the big-endian encoding
        first_7_bits = nonce >> 25  # Shift right by 25 to keep the first 7 bits
    elif endian == 'little':
        # Extract the first 7 bits from the little-endian encoding
        first_7_bits = nonce & 0x7F  # Mask with 0b01111111 to keep the first 7 bits
    else:
        raise ValueError("Invalid endian specified. Use 'big' or 'little'.")
    
    return first_7_bits

# Example usage:
nonce = 0xAABBCCDD  # Example nonce value
print("First 7 bits (big endian):", extract_first_7_bits(nonce, endian='big'))
print("First 7 bits (little endian):", extract_first_7_bits(nonce, endian='little'))

def test_get_byte0():
    # Test big endian
    assert get_byte0(0xAABBCCDD, endian='big') == 0xAA
    # Test little endian
    assert get_byte0(0xAABBCCDD, endian='little') == 0xDD

def test_get_byte0_array():
    # Test big endian
    nonce_array = np.array([0xAABBCCDD, 0x11223344, 0xDEADBEEF], dtype=np.uint32)
    expected_big_endian = np.array([0xAA, 0x11, 0xDE], dtype=np.uint8)
    np_test.assert_array_equal(get_byte0_array(nonce_array, endian='big'), expected_big_endian)
    
    # Test little endian
    expected_little_endian = np.array([0xDD, 0x44, 0xEF], dtype=np.uint8)
    np_test.assert_array_equal(get_byte0_array(nonce_array, endian='little'), expected_little_endian)

# Run the test functions
test_get_byte0()
test_get_byte0_array()