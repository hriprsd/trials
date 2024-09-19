"""
This script updates secrets in actions secrets space - The secret is encrypted using nacl before updating in github 
To invoke the script from the command line, run the following command:

Install the required packages:
pip install -q --root-user-action=ignore requests pynacl
Run the script:
python update-actions-secret.py "<secret_name>" "<secret_value>"

If the secret already exists, it will be updated, else a new secret will be created.
"""
from base64 import b64encode
from nacl import encoding, public
import sys, os, requests, json

response = requests.get(
    "https://api.github.com/orgs/<org-name>/actions/secrets/public-key",
    headers={"Authorization": f"Bearer {os.environ.get('GHEC_TOKEN')}"})
# Get the public key and key_id from the GitHub API
key = json.loads(response.text)['key']
key_id = json.loads(response.text)['key_id']

# Encrypting the secret with GHEC public key
def encrypt(public_key: str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode('utf-8')

# POSTing encrypted secret to GHEC actions secrets
# key is updated if it exists, or else a new key is created
def update_actions_secret(key_id: str, secret_name: str, encrypted_value: str):
  """Update a secret in a GitHub repository."""
  response = requests.put(
    f"https://api.github.com/orgs/<org-name>/actions/secrets/{secret_name}",
    headers={"Authorization": f"Bearer {os.environ.get('GHEC_TOKEN')}",
             "Accept": "application/vnd.github.v3+json"},
    json={"encrypted_value": encrypted_value, "key_id": key_id, "visibility": "all"})
  if response.status_code == 204:
    print(f"result :: {secret_name} secret updated successfully")
  else:
    print(f"result :: error updating {secret_name} secret")
    print(response.text)

if __name__ == "__main__":
  args = sys.argv
  print(f"action :: Encrypting secret...")
  encrypted_secret = encrypt(key, args[2])
  print(f"action :: Updating secret...")
  update_actions_secret(key_id, args[1], encrypted_secret)
