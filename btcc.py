#!/usr/bin/env python3
# coding=utf8

import threading
from bitcoinlib.keys import Key, generate_key

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
    # Generate a random Bitcoin private key within the specified keyspace range
    while True:
        private_key = generate_key()
        if keyspace_start <= int(private_key.wif()) <= keyspace_end:
            return private_key

def find_collision(thread_num):
    while True:
        # Generate a random Bitcoin private key within the keyspace range
        private_key = generate_private_key()

        # Compute the Bitcoin address from the private key
        address = private_key.address()

        if address == target_address:
            with print_lock:
                print(f"Collision Found by Thread {thread_num}")
                print(f"Bitcoin Address: {address}")
                print(f"Private Key (WIF): {private_key.wif()}")
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
