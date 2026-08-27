#!/usr/bin/env python3
"""Interactively create the AutoDL email secret file without echoing it."""

import argparse
import getpass
import os
from pathlib import Path

DEFAULT_PATH = "/root/autodl-tmp/WMKD_Benchmark_data/secrets/email.env"

parser = argparse.ArgumentParser()
parser.add_argument("--path", default=DEFAULT_PATH)
args = parser.parse_args()
path = Path(args.path)
password = getpass.getpass("Gmail 16-character App Password (input hidden): ").replace(" ", "")
if not password:
    raise SystemExit("No password entered; credential was not changed.")
if len(password) != 16:
    raise SystemExit("Expected a 16-character Google App Password; credential was not changed.")
path.parent.mkdir(parents=True, exist_ok=True)
temp = path.with_suffix(path.suffix + ".tmp")
fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as output:
    output.write("WMKD_EMAIL_SENDER=EasonHanYichen@gmail.com\n")
    output.write("WMKD_EMAIL_RECIPIENT=21672330@students.latrobe.edu.au\n")
    output.write(f"WMKD_GMAIL_APP_PASSWORD={password}\n")
os.chmod(temp, 0o600)
temp.replace(path)
os.chmod(path, 0o600)
print("Email credential configured successfully.")
