from django.utils import timezone
from django.db import models
from cryptography.fernet import Fernet
import hashlib


class AdminProfile(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_address = models.CharField(max_length=200)
    admin_password = models.CharField(max_length=100)
    admin_acc_created_time = models.DateTimeField(auto_now_add=True)


class Voter(models.Model):
    voter_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=50, null=False)
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)
    mobile = models.CharField(max_length=15, unique=True, null=False)
    dob = models.DateField()
    password = models.CharField(max_length=128, null=False)
    is_registered = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)


class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    name = models.CharField(max_length=255)
    party = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=255, default=0)
    votes = models.IntegerField(default=0)  # For demonstration only, not for secure voting
    image = models.ImageField(upload_to='static/candidates/', null=True, blank=True)

    def __str__(self):
        return self.name


class VotePhase(models.Model):
    phase = models.CharField(max_length=20,
                             choices=[('registration', 'Registration'), ('voting', 'Voting'), ('closed', 'Closed')],
                             default='registration')

    def __str__(self):
        return self.phase


class Block(models.Model):
    encrypted_voter_id = models.BinaryField()
    encrypted_candidate_id = models.BinaryField()
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_hash = models.BinaryField()
    block_hash = models.BinaryField()

    def __str__(self):
        return f"Block {self.encrypted_voter_id}"

    @staticmethod
    def encrypt_data(data, key):
        f = Fernet(key)
        return f.encrypt(data.encode())

    @staticmethod
    def decrypt_data(self, data, key):
        f = Fernet(key)
        return f.decrypt(data).decode()

    def calculate_hash(self):
        data = (str(self.encrypted_voter_id) + str(self.encrypted_candidate_id) + str(self.previous_hash)).encode()
        return hashlib.sha256(data).digest()

    @staticmethod
    def create_block(voter_id, candidate_id, previous_hash, key):
        f = Fernet(key)
        encrypted_voter_id = Block.encrypt_data(key=key)
        encrypted_candidate_id = Block.encrypt_data(key=key)
        block = Block(
            encrypted_voter_id=encrypted_voter_id,
            encrypted_candidate_id=encrypted_candidate_id,
            previous_hash=previous_hash
        )
        block.block_hash = block.calculate_hash()
        return block


class ElectionResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    election_name = models.CharField(max_length=255)
    candidate_name = models.CharField(max_length=255)
    total_votes = models.IntegerField()
    result_declaration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.election_name} - {self.candidate_name}"



class ElectionResultStatus(models.Model):
    result_declared = models.BooleanField(default=False)
    result_calculated = models.BooleanField(default=False)

    def __str__(self):
        return "Result Declared" if self.result_declared else "Result Not Declared"


class EncryptionKey(models.Model):
    key = models.BinaryField()

    @staticmethod
    def generate_key():
        # Generate a new Fernet key
        key = Fernet.generate_key()
        return key

    def encrypt_data(self, data):
        f = Fernet(self.key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        f = Fernet(self.key)
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data
