import hashlib

from cryptography.fernet import Fernet
from voter_admin.models import Block
from voter_admin.models import EncryptionKey


def create_block(voter_id, candidate_id, previous_hash, key):
    encrypted_voter_id = encrypt_data(data=voter_id, key=key)
    encrypted_candidate_id = encrypt_data(data=candidate_id, key=key)
    block = Block(
        encrypted_voter_id=encrypted_voter_id,
        encrypted_candidate_id=encrypted_candidate_id,
        previous_hash=previous_hash
    )
    block.block_hash = block.calculate_hash()
    return block


def encrypt_data(data, key):
    print(key)
    f = Fernet(key)
    print(f)
    return f.encrypt(data.encode())


def decrypt_data(data):
    print("DECRYPT DATA ")
    key = read_key_from_file()
    print("DATA = ",data)
    print("KEY = ",key)
    f = Fernet(key)
    print("FERNET KEY = ",f)
    print("NOT DECRYPTED")
    return f.decrypt(data).decode()


def calculate_hash(self):
    data = (str(self.encrypted_voter_id) + str(self.encrypted_candidate_id) + str(self.previous_hash) + str(
        self.nonce)).encode()
    return hashlib.sha256(data).digest()


def election_generate_key():
    key = Fernet.generate_key()
    filename = 'key.txt'
    with open(filename, 'wb') as f:
        f.write(key)
    return key


def read_key_from_file():
    filename = 'key.txt'
    with open(filename, 'rb') as f:
        return f.read()
