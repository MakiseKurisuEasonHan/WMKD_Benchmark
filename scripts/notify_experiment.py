#!/usr/bin/env python3
"""Best-effort, duplicate-safe WMKD experiment email notifications."""

import argparse
import datetime as dt
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import socket
import ssl
import sys

DEFAULT_SENDER = "EasonHanYichen@gmail.com"
DEFAULT_RECIPIENT = "21672330@students.latrobe.edu.au"
DEFAULT_SECRET_FILE = "/root/autodl-tmp/WMKD_Benchmark_data/secrets/email.env"
DEFAULT_STATE_ROOT = "/root/autodl-tmp/WMKD_Benchmark_data/notifications"
VALID_EVENTS = ("STARTED", "COMPLETED", "FAILED", "INTERRUPTED")


def load_secret_environment(path):
    secret_path = Path(path)
    if not secret_path.exists():
        return
    mode = secret_path.stat().st_mode & 0o777
    if mode & 0o077:
        raise PermissionError(f"secret file permissions must be 600, found {mode:o}")
    for line in secret_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in {"WMKD_GMAIL_APP_PASSWORD", "WMKD_EMAIL_SENDER", "WMKD_EMAIL_RECIPIENT"}:
            os.environ.setdefault(key, value)


def build_message(args, sender, recipient):
    timestamp = args.time or dt.datetime.now().astimezone().isoformat()
    hostname = args.host or socket.gethostname()
    fields = [
        ("Project", "WMKD_Benchmark"), ("Experiment", args.experiment),
        ("Run ID", args.run_id), ("Event", args.event), ("Time", timestamp),
        ("Host", hostname), ("Stage", args.stage or "unknown"),
        ("PID", args.pid or "not available"),
        ("Exit code", args.exit_code if args.exit_code is not None else "not available"),
        ("Status", args.status or args.event.lower()),
        ("Log path", args.log_path or "not available"),
        ("Status file", args.status_file or "not available"),
        ("Short message", args.message or "No additional message."),
    ]
    if args.error_summary:
        fields.append(("Error summary (tail)", args.error_summary))
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = args.subject or f"[WMKD] {args.experiment} {args.event}"
    message.set_content("\n\n".join(f"{key}:\n{value}" for key, value in fields))
    return message


def state_path_for(args):
    if args.state_file:
        return Path(args.state_file)
    return Path(args.state_root) / args.run_id / "notification_state.json"


def read_state(path):
    if not path.exists():
        return {event: False for event in VALID_EVENTS}
    data = json.loads(path.read_text())
    return {event: bool(data.get(event, False)) for event in VALID_EVENTS}


def write_record(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.replace(path)


def notify(args):
    try:
        load_secret_environment(args.secret_file)
        password = os.environ.get("WMKD_GMAIL_APP_PASSWORD")
        if not password:
            print("email notification disabled: WMKD_GMAIL_APP_PASSWORD is not configured")
            return 0
        sender = os.environ.get("WMKD_EMAIL_SENDER", DEFAULT_SENDER)
        recipient = os.environ.get("WMKD_EMAIL_RECIPIENT", DEFAULT_RECIPIENT)
        state_path = state_path_for(args)
        state = read_state(state_path)
        if state.get(args.event):
            print(f"email notification skipped: {args.run_id} {args.event} was already sent")
            return 0
        message = build_message(args, sender, recipient)
        if args.dry_run:
            print(f"email notification dry-run ready: {message['Subject']}")
            return 0
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=args.timeout) as smtp:
            smtp.login(sender, password)
            smtp.send_message(message)
        state[args.event] = True
        state["last_sent_at"] = dt.datetime.now().astimezone().isoformat()
        write_record(state_path, state)
        print(f"email notification sent: {args.run_id} {args.event}")
    except Exception as exc:  # notifications must never fail a scientific pipeline
        failure_path = Path(args.failure_record or (str(state_path_for(args)) + ".failure.json"))
        record = {
            "run_id": args.run_id, "event": args.event,
            "time": dt.datetime.now().astimezone().isoformat(),
            "error_type": type(exc).__name__, "error": str(exc),
        }
        try:
            write_record(failure_path, record)
        except Exception:
            pass
        print(f"email notification failed (experiment unaffected): {type(exc).__name__}: {exc}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, choices=VALID_EVENTS)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stage")
    parser.add_argument("--message")
    parser.add_argument("--pid")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--status")
    parser.add_argument("--log-path")
    parser.add_argument("--status-file")
    parser.add_argument("--error-summary")
    parser.add_argument("--time")
    parser.add_argument("--host")
    parser.add_argument("--subject")
    parser.add_argument("--secret-file", default=DEFAULT_SECRET_FILE)
    parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    parser.add_argument("--state-file")
    parser.add_argument("--failure-record")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser


if __name__ == "__main__":
    sys.exit(notify(build_parser().parse_args()))
