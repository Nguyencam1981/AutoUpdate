import os
import hmac
import hashlib
import logging
import json
import subprocess
from threading import Thread
from flask import Flask, request, abort, jsonify

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

GITHUB_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
# Optional: repo path and service name for the updater script
REPO_PATH = os.environ.get("REPO_PATH", "")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "")


def verify_signature(secret: str, payload_body: bytes, header_signature: str) -> bool:
    if not header_signature:
        return False
    try:
        algo, signature = header_signature.split('=', 1)
    except Exception:
        return False
    if algo != 'sha256':
        return False
    mac = hmac.new(secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def run_updater_async(event_name: str, payload: dict):
    Thread(target=run_updater, args=(event_name, payload), daemon=True).start()


def run_updater(event_name: str, payload: dict):
    """
    Call the PowerShell updater script. This will run the script and log output.
    The PS script path is relative to this file: ../updater/updater.ps1
    """
    here = os.path.dirname(os.path.abspath(__file__))
    ps_path = os.path.abspath(os.path.join(here, '..', 'updater', 'updater.ps1'))
    if not os.path.exists(ps_path):
        LOG.error("Updater script not found at %s", ps_path)
        return

    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", ps_path,
        REPO_PATH,
        SERVICE_NAME,
    ]
    LOG.info("Running updater: %s", cmd)
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        LOG.info("Updater exit code: %s", completed.returncode)
        LOG.info("Updater stdout: %s", completed.stdout)
        LOG.info("Updater stderr: %s", completed.stderr)
    except Exception as e:
        LOG.exception("Failed to run updater: %s", e)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/webhook', methods=['POST'])
def webhook():
    header_signature = request.headers.get('X-Hub-Signature-256', '')
    event = request.headers.get('X-GitHub-Event', 'unknown')
    body = request.get_data()

    if not GITHUB_SECRET:
        LOG.warning("GITHUB_WEBHOOK_SECRET not set; rejecting request")
        abort(403)

    if not verify_signature(GITHUB_SECRET, body, header_signature):
        LOG.warning("Invalid signature for event %s", event)
        abort(403)

    try:
        payload = request.get_json()
    except Exception:
        payload = {}

    LOG.info("Received GitHub event: %s", event)

    # Only act on push or release (you can customize)
    if event in ('push', 'release'):
        run_updater_async(event, payload)
        return jsonify({"status": "updater triggered", "event": event}), 202

    return jsonify({"status": "ignored", "event": event}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
