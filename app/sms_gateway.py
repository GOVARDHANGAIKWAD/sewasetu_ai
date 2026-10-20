# -*- coding: utf-8 -*-
"""
Embedded simulated SMS gateway for Sewa Setu.
Can run both as a Flask blueprint within the main portal app AND as a standalone service on port 8025.
"""

import time
import random
from flask import Blueprint, request, jsonify, render_template_string

smsgw_bp = Blueprint("smsgw_internal", __name__)

MESSAGES = []  # {id, to, text, sent_at, delivery_at}
DELAY_MIN = 1
DELAY_MAX = 3

CONSOLE_HTML = """
<!doctype html>
<html>
<head>
  <title>PurvSMS Console — Sewa Setu Simulated Telecom</title>
  <meta http-equiv="refresh" content="3">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 24px; background: #0f172a; color: #f8fafc; }
    h2 { color: #38bdf8; margin-bottom: 6px; }
    p.sub { color: #94a3b8; font-size: 14px; margin-top: 0; }
    .badge { display: inline-block; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
    .delivered { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
    .queued { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }
    table { border-collapse: separate; border-spacing: 0; background: #1e293b; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
    th { background: #0f172a; color: #94a3b8; padding: 10px 14px; font-size: 13px; text-align: left; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #334155; }
    td { padding: 10px 14px; font-size: 14px; border-bottom: 1px solid #1e293b; }
    tr:nth-child(even) { background: rgba(255, 255, 255, 0.02); }
    .otp-code { font-family: monospace; font-weight: bold; color: #f43f5e; background: rgba(244, 63, 94, 0.15); padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <h2>PurvSMS Gateway Console (Simulated Telecom)</h2>
  <p class="sub">Messages appear below once delivered across the simulated carrier network. Auto-refreshes every 3s.</p>
  <table>
    <thead>
      <tr>
        <th style="width: 60px;">#</th>
        <th style="width: 140px;">Recipient</th>
        <th>Message Content</th>
        <th style="width: 120px;">Timestamp</th>
        <th style="width: 140px;">Status</th>
      </tr>
    </thead>
    <tbody>
      {% for m in messages %}
      <tr>
        <td>{{m.id}}</td>
        <td style="font-weight: 500; color: #e2e8f0;">{{m.to}}</td>
        <td>
          {% if m.delivered %}
            {{m.text}}
          {% else %}
            <i style="color: #64748b;">(in transit over cellular network...)</i>
          {% endif %}
        </td>
        <td style="color: #94a3b8;">{{m.sent_hhmm}}</td>
        <td>
          {% if m.delivered %}
            <span class="badge delivered">✓ Delivered</span>
          {% else %}
            <span class="badge queued">⏳ Queued (~{{m.eta}}s)</span>
          {% endif %}
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="5" style="text-align: center; color: #64748b; padding: 24px;">No messages sent yet.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""


def record_sms(to, text):
    """Programmatic helper to enqueue an SMS directly without network overhead."""
    now = time.time()
    msg = {
        "id": len(MESSAGES) + 1,
        "to": str(to).strip(),
        "text": text,
        "sent_at": now,
        "delivery_at": now + random.randint(DELAY_MIN, DELAY_MAX),
    }
    MESSAGES.append(msg)
    return msg["id"]


def get_latest_otp(mobile):
    """Helper to find the most recent delivered OTP code for a mobile number."""
    import re
    now = time.time()
    for m in reversed(MESSAGES):
        if m["to"] == str(mobile).strip() and now >= m["delivery_at"]:
            match = re.search(r'\b(\d{6})\b', m["text"])
            if match:
                return match.group(1)
    return None


@smsgw_bp.route("/api/send", methods=["POST"])
def send():
    data = request.get_json(force=True, silent=True) or request.form
    to = data.get("to", "")
    text = data.get("text", "")
    if not to or not text:
        return jsonify({"status": "error", "reason": "to and text required"}), 400
    msg_id = record_sms(to, text)
    return jsonify({"status": "queued", "id": msg_id})


@smsgw_bp.route("/api/messages")
def messages():
    to = request.args.get("to", "")
    now = time.time()
    out = []
    for m in MESSAGES:
        if to and m["to"] != str(to).strip():
            continue
        out.append({
            "id": m["id"],
            "to": m["to"],
            "text": m["text"] if now >= m["delivery_at"] else None,
            "delivered": now >= m["delivery_at"],
            "sent_at": m["sent_at"],
            "delivery_at": m["delivery_at"],
        })
    return jsonify({"messages": out})


@smsgw_bp.route("/")
def console():
    now = time.time()
    view = []
    for m in reversed(MESSAGES[-100:]):
        view.append({
            "id": m["id"],
            "to": m["to"],
            "text": m["text"],
            "sent_hhmm": time.strftime("%H:%M:%S", time.localtime(m["sent_at"])),
            "delivered": now >= m["delivery_at"],
            "eta": max(0, int(m["delivery_at"] - now)),
        })
    return render_template_string(CONSOLE_HTML, messages=view)
