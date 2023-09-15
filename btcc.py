#!/usr/bin/env python3
# coding=utf8

import threading
import pybitcoin as bitcoin

# Define the keyspace range
keyspace_start = 0x8000000000000000
keyspace_end = 0xFFFFFFFFFFFFFFFF

# Define the target Bitcoin address
target_address = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"

# Define the number of threads for parallel processing
num_threads = 4  # Adjust as needed

# Create a lock to ensure safe printing
print_lock = threading.Lock()

def generate_private_key():
    # Generate a random 32-byte private key (256 bits) within the specified keyspace range
    return int.to_bytes(bitcoin.random_key(), length=32, byteorder='big')

def find_collision(thread_num):
    while True:
        # Generate a random private key within the keyspace range
        private_key_bytes = generate_private_key()
        private_key_int = int.from_bytes(private_key_bytes, byteorder='big')

        if keyspace_start <= private_key_int <= keyspace_end:
            # Compute the Bitcoin address from the private key
            public_key = bitcoin.privkey_to_pubkey(private_key_bytes)
            address = bitcoin.pubkey_to_address(public_key)

            if address == target_address:
                with print_lock:
                    print(f"Collision Found by Thread {thread_num}")
                    print(f"Bitcoin Address: {address}")
                    print(f"Private Key (hex): {private_key_bytes.hex()}")
                return

if __name__ == '__main__':
    # Create and start multiple threads for collision search
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=find_collision, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
