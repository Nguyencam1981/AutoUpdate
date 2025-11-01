import hmac
import hashlib
from webhook_receiver.app import verify_signature


def test_verify_signature():
    secret = "mysecret"
    payload = b'{"ref": "refs/heads/main"}'
    mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
    header = 'sha256=' + mac.hexdigest()
    assert verify_signature(secret, payload, header)


def test_verify_signature_fail():
    secret = "mysecret"
    payload = b'{"ref": "refs/heads/main"}'
    bad_header = 'sha256=' + '0'*64
    assert not verify_signature(secret, payload, bad_header)
