# -*- coding: utf-8 -*-
"""
Sewa Setu — Unified Local Server Runner.
Runs the complete Old Age Pension portal, both MCP servers, the simulated SMS gateway,
the 100k-row database, and the evaluation dashboard on http://localhost:8000.
"""

import os
import sys
import time
import threading

# Add app to pythonpath
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")
sys.path.insert(0, APP_DIR)

# Set environment defaults if not set
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")
os.environ.setdefault("PUBLIC_BASE_URL", "http://localhost:8000")

# Ensure upload directory exists
upload_dir = os.path.join(BASE_DIR, "uploads")
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(os.path.join(upload_dir, "ack"), exist_ok=True)

import db_adapter
import app as portal_app
import scripts.deemed_approval as deemed_approval_script


def run_scheduler_loop():
    """Background thread that runs the deemed approval check periodically."""
    time.sleep(5)  # initial boot wait
    while True:
        try:
            deemed_approval_script.main()
        except Exception as e:
            print(f"[Scheduler] Deemed approval job error: {e}")
        time.sleep(300)  # check every 5 minutes


def print_banner():
    banner = r"""
================================================================================
   SEWA SETU — OLD AGE PENSION PORTAL & AGENTIC MCP SERVERS (PURVANCHAL)
================================================================================
  Portal Home:              http://localhost:8000
  Citizen MCP Server:       http://localhost:8000/mcp/citizen
  Citizen MCP SSE:          http://localhost:8000/mcp/citizen/sse
  Officer MCP Server:       http://localhost:8000/mcp/officer
  Officer MCP SSE:          http://localhost:8000/mcp/officer/sse
  Evaluation Dashboard:     http://localhost:8000/eval-dashboard
  Status Portal:            http://localhost:8000/status
  Admin Dashboard:          http://localhost:8000/admin  (admin / admin123)
  Simulated SMS Gateway:    http://localhost:8000/__gateway/
================================================================================
"""
    print(banner)


if __name__ == "__main__":
    print_banner()

    # Pre-verify database initialization
    print("[Server] Verifying database and seed records...")
    db_conn = db_adapter.get_connection("localhost", 5432, "sewasetu", "sewasetu", "sewasetu123")
    cur = db_conn.cursor()
    cur.execute("SELECT count(*) FROM applications")
    count = cur.fetchone()[0]
    print(f"[Server] Database ready with {count} application records.")
    db_conn.close()

    # Pre-warm evaluation dashboard benchmark
    print("[Server] Initializing Evaluation Dashboard benchmark cache...")
    import eval_dashboard
    eval_dashboard.CACHED_EVAL_DATA = eval_dashboard.run_all_evals()
    print(f"[Server] Benchmark suite verified: {eval_dashboard.CACHED_EVAL_DATA['pass_rate_percent']}% pass rate across {eval_dashboard.CACHED_EVAL_DATA['total_assertions']} assertions.")

    # Start background scheduler
    sched_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    sched_thread.start()
    print("[Server] Statutory SLA Deemed Approval scheduler active.")

    # Run the server
    print("[Server] Starting Sewa Setu on http://0.0.0.0:8000...")
    portal_app.app.run(host="0.0.0.0", port=8000, debug=False)
