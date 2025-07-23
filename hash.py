# generate a Murmur3 hash for a given string
import mmh3

def compute_murmur3_hash(key):
    # Compute 32-bit Murmur3 hash with seed 0
    hash_value = mmh3.hash(key.encode('utf-8'), seed=0)
    return hash_value

# Input string
key = "john_doe"
hash_result = compute_murmur3_hash(key)
print(f"Murmur3 hash for '{key}': {hash_result}")