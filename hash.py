import hashlib

def file_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):  # read in 4KB chunks
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


file_name = "C:/Users/lostw/Downloads/Important Notice 26 August 2025.pdf"
# Example usage
print(file_sha256(file_name))
# c9400827ae3cef3c60e8686d6625f9d36ddd5646cbe3652439b5aa754b544d84
# c9400827ae3cef3c60e8686d6625f9d36ddd5646cbe3652439b5aa754b544d84