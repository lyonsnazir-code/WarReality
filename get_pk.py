from eth_account import Account
from mnemonic import Mnemonic

# Enable HD wallet features for standard BIP-44 derivation (Ethereum path: m/44'/60'/0'/0/0)
Account.enable_unaudited_hdwallet_features()

mnemonic_phrase = "athlete excess above length repair grant icon crash course token digital embark"

# Derive the account and private key from your seed phrase
account = Account.from_mnemonic(mnemonic_phrase, account_path="m/44'/60'/0'/0/0")

print(f"\n[SUCCESS] Your Address: {account.address}")
print(f"[SUCCESS] Your Private Key: {account._private_key.hex()}\n")