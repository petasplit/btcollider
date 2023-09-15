#!/usr/bin/env python3
# coding=utf8

import threading
from ecdsa import SigningKey, SECP256k1
import hashlib
import base58
from tqdm import tqdm

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
    while True:
        private_key = SigningKey.generate(curve=SECP256k1)
        private_key_int = int.from_bytes(private_key.to_string(), byteorder='big')

        if keyspace_start <= private_key_int <= keyspace_end:
            return private_key

def compute_public_key(private_key):
    return private_key.get_verifying_key()

def compute_bitcoin_address(public_key):
    sha256_hash = public_key.to_string()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    address = b'\x00' + ripemd160_hash  # Assuming a Mainnet address (0x00 prefix)
    checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
    address += checksum
    return base58.b58encode(address)

def find_collision(thread_num, progress_bar):
    while True:
        private_key = generate_private_key()
        public_key = compute_public_key(private_key)
        address = compute_bitcoin_address(public_key).decode()

        if address == target_address:
            with print_lock:
                print(f"Collision Found by Thread {thread_num}")
                print(f"Bitcoin Address: {address}")
                print(f"Private Key (hex): {private_key.to_string().hex()}")
            return

        # Update the progress bar
        progress_bar.update(1)

if __name__ == '__main__':
    # Create a progress bar
    with tqdm(total=num_threads, desc="Searching", unit=" thread") as progress_bar:
        # Create and start multiple threads for collision search
        threads = [5]
        for i in range(num_threads):
            thread = threading.Thread(target=find_collision, args=(i, progress_bar))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
