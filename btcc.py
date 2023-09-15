#!/usr/bin/env python3
# coding=utf8

import threading
from ecdsa import SigningKey, SECP256k1
import hashlib
import base58
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Define the keyspace range
keyspace_start = 0x8000000000000000
keyspace_end = 0xFFFFFFFFFFFFFFFF

# Define the target Bitcoin address
target_address = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"

# Define the number of threads for parallel processing
num_threads = 4  # Adjust as needed

# Number of address computations per batch
batch_size = 100

# Create a lock to ensure safe printing
print_lock = threading.Lock()

def generate_private_key():
    while True:
        private_key = SigningKey.generate(curve=SECP256k1)
        private_key_int = int.from_bytes(private_key.to_string(), byteorder='big')

        if keyspace_start <= private_key_int <= keyspace_end:
            return private_key, private_key_int

def compute_public_key(private_key):
    return private_key.get_verifying_key()

def compute_bitcoin_address(public_key):
    sha256_hash = public_key.to_string()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    address = b'\x00' + ripemd160_hash  # Assuming a Mainnet address (0x00 prefix)
    checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
    address += checksum
    return base58.b58encode(address)

def search_batch(thread_num, start_range, end_range):
    collisions = []
    for _ in range(batch_size):
        private_key, private_key_int = generate_private_key()
        public_key = compute_public_key(private_key)
        address = compute_bitcoin_address(public_key).decode()

        if address == target_address:
            with print_lock:
                collisions.append(private_key_int)
                print(f"Collision Found by Thread {thread_num}")
                print(f"Bitcoin Address: {address}")
                print(f"Private Key (hex): {private_key.to_string().hex()}")
                print(f"Collided Keyspace Range: 0x{start_range:x} - 0x{end_range:x}")
    return collisions

if __name__ == '__main__':
    # Create a progress bar
    with tqdm(total=num_threads, desc="Threads Completed", unit=" thread") as progress_bar:
        # Create and start multiple threads for collision search
        threads = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(num_threads):
                start_range = i * (keyspace_end - keyspace_start) // num_threads + keyspace_start
                end_range = (i + 1) * (keyspace_end - keyspace_start) // num_threads + keyspace_start
                threads.append(executor.submit(search_batch, i, start_range, end_range))

        # Wait for all threads to finish and collect collisions
        collisions = []
        for thread in threads:
            collisions.extend(thread.result())

    # Display the keyspace ranges of collisions
    print("\nCollisions occurred in the following keyspace ranges:")
    for collision in collisions:
        start_range = max(keyspace_start, collision - 1)
        end_range = min(keyspace_end, collision + 1)
        print(f"Keyspace Range: 0x{start_range:x} - 0x{end_range:x}")
