"""Built-in lightweight Web Server and REST API for airun profiler.

Serves an interactive executive dashboard and REST APIs directly from the local SQLite trace store.
"""

import json
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from airun.analysis.analyzer import analyze_spans
from airun.analysis.comparator import compare_traces
from airun.store import get_trace_store


class AirunServerHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler providing REST API and single-page executive web UI."""

    server_version = "airun-server/0.1.1"

    def _send_json(self, data: Any, status: int = 200):
        """Helper to send JSON response."""
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html: str, status: int = 200):
        """Helper to send HTML response."""
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        """Handle incoming GET requests."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Health check endpoint (for AWS ALB / Kubernetes liveness probe)
        if path == "/healthz" or path == "/health":
            self._send_json({"status": "ok", "version": "0.1.1", "timestamp": datetime.now(timezone.utc).isoformat()})
            return

        # API: List all trace summaries
        if path == "/api/traces":
            store = get_trace_store()
            limit = int(query_params.get("limit", [50])[0])
            summaries = store.list_traces(limit=limit)
            self._send_json([s.model_dump() for s in summaries])
            return

        # API: High-level KPI summary
        if path == "/api/summary":
            store = get_trace_store()
            summaries = store.list_traces(limit=500)
            total_traces = len(summaries)
            total_cost = sum(s.total_cost_usd or 0.0 for s in summaries)
            total_tokens = sum(s.total_tokens or 0 for s in summaries)
            avg_duration_ms = (sum(s.total_duration_ms or 0.0 for s in summaries) / total_traces) if total_traces > 0 else 0.0
            successful_traces = [s for s in summaries if str(s.outcome).lower() in ("success", "spanstatus.success")]
            success_rate = (len(successful_traces) / total_traces * 100.0) if total_traces > 0 else 100.0
            wasted_cost = sum(s.wasted_cost_usd or 0.0 for s in summaries)

            self._send_json({
                "total_traces": total_traces,
                "total_cost_usd": round(total_cost, 4),
                "wasted_cost_usd": round(wasted_cost, 4),
                "total_tokens": total_tokens,
                "avg_duration_ms": round(avg_duration_ms, 1),
                "success_rate": round(success_rate, 1),
            })
            return

        # API: Single trace detail with spans, DAG, and diagnostic findings
        if path.startswith("/api/traces/"):
            trace_id = path.split("/api/traces/")[1]
            store = get_trace_store()
            trace_record = store.get_trace(trace_id)
            if not trace_record or not trace_record.spans:
                self._send_json({"error": f"Trace '{trace_id}' not found"}, status=404)
                return

            spans = trace_record.spans
            summary = trace_record.summary or analyze_spans(spans)
            findings = summary.diagnostic_findings or []

            self._send_json({
                "trace_id": trace_record.trace_id,
                "summary": summary.model_dump(),
                "findings": [f.model_dump() for f in findings],
                "spans": [s.model_dump() for s in spans],
                "critical_path_ms": summary.critical_path_ms,
                "total_sequential_ms": summary.total_duration_ms,
            })
            return

        # API: Compare two traces
        if path == "/api/compare":
            id1 = query_params.get("id1", [None])[0]
            id2 = query_params.get("id2", [None])[0]
            if not id1 or not id2:
                self._send_json({"error": "Both id1 and id2 parameters are required for comparison"}, status=400)
                return

            store = get_trace_store()
            rec1 = store.get_trace(id1)
            rec2 = store.get_trace(id2)
            if not rec1 or not rec2:
                self._send_json({"error": "One or both traces not found in storage"}, status=404)
                return

            sum1 = rec1.summary or analyze_spans(rec1.spans)
            sum2 = rec2.summary or analyze_spans(rec2.spans)
            comparison = compare_traces(sum1, sum2)
            self._send_json(comparison.model_dump())
            return

        # Default: Serve the single-page HTML/CSS/JS dashboard
        self._send_html(get_dashboard_html())

    def log_message(self, format, *args):
        """Suppress default stdout logging for clean console operation."""
        return


class ResilientHTTPServer(ThreadingHTTPServer):
    """Threading HTTP server with address reuse enabled."""
    allow_reuse_address = True


def start_server(host: str = "127.0.0.1", port: int = 8765):
    """Starts the airun web server and listens for requests with automatic fallback."""
    candidate_hosts = [host]
    if host == "0.0.0.0" and "127.0.0.1" not in candidate_hosts:
        candidate_hosts.append("127.0.0.1")
    elif host == "127.0.0.1" and "localhost" not in candidate_hosts:
        candidate_hosts.append("localhost")

    candidate_ports = [port, 8765, 8080, 5000, 9000, 3000]
    # Remove duplicates preserving order
    candidate_ports = list(dict.fromkeys(candidate_ports))

    httpd = None
    active_host = host
    active_port = port

    for h in candidate_hosts:
        for p in candidate_ports:
            try:
                server_address = (h, p)
                httpd = ResilientHTTPServer(server_address, AirunServerHandler)
                active_host = h
                active_port = p
                break
            except (PermissionError, OSError):
                continue
        if httpd is not None:
            break

    if httpd is None:
        print(f"\n[!] Error: Unable to bind to any available network port ({candidate_ports}).")
        return

    print("\n" + "=" * 60)
    print("  🚀 airun AI Runtime Profiler & Executive Dashboard")
    print("=" * 60)
    print("  * Status:        ONLINE")
    print(f"  * Local Web UI:  http://localhost:{active_port}")
    if active_host not in ("127.0.0.1", "localhost"):
        print(f"  * Network URL:   http://{active_host}:{active_port}")
    print(f"  * Health check:  http://localhost:{active_port}/healthz")
    print("=" * 60)
    print(">> Press Ctrl+C to stop the dashboard server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n>> Stopping airun server...")
        httpd.server_close()


def get_dashboard_html() -> str:
    """Returns the self-contained modern dark-mode Executive Dashboard HTML/JS."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>airun — AI Runtime Profiler & Executive Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --card-hover: #1e293b;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --critical: #ef4444;
      --critical-bg: rgba(239, 68, 68, 0.15);
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.15);
      --info: #06b6d4;
      --info-bg: rgba(6, 182, 212, 0.15);
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.15);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      line-height: 1.5;
      padding-bottom: 60px;
    }
    .container { max-width: 1380px; margin: 0 auto; padding: 24px; }
    header {
      display: flex; justify-content: space-between; align-items: center;
      padding-bottom: 24px; border-bottom: 1px solid var(--card-border); margin-bottom: 28px;
    }
    .logo-area { display: flex; align-items: center; gap: 14px; }
    .logo-badge {
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      color: white; font-weight: 700; font-size: 1.1rem; padding: 6px 14px;
      border-radius: 8px; font-family: 'JetBrains Mono', monospace;
    }
    .header-title h1 { font-size: 1.4rem; font-weight: 700; }
    .header-title p { font-size: 0.85rem; color: var(--text-muted); }
    .nav-actions { display: flex; gap: 12px; }
    .btn {
      background: var(--card-bg); border: 1px solid var(--card-border); color: var(--text-main);
      padding: 8px 16px; border-radius: 6px; font-size: 0.85rem; cursor: pointer;
      display: inline-flex; align-items: center; gap: 8px; font-weight: 500;
      transition: all 0.15s ease;
    }
    .btn:hover { background: var(--card-hover); border-color: var(--accent); }
    .btn-primary { background: var(--accent); border-color: var(--accent); color: white; }
    .btn-primary:hover { background: var(--accent-hover); }

    /* KPI Grid */
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
    .kpi-card {
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 18px; position: relative; overflow: hidden;
    }
    .kpi-card::before {
      content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
      background: var(--accent);
    }
    .kpi-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; margin-bottom: 6px; }
    .kpi-value { font-size: 1.6rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .kpi-sub { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }

    /* Main layout: Table + Detail Split */
    .main-split { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    @media (max-width: 1024px) { .main-split { grid-template-columns: 1fr; } }

    .panel {
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 20px;
    }
    .panel-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--card-border);
    }
    .panel-title { font-size: 1.05rem; font-weight: 600; }

    /* Traces Table */
    .table-container { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem; }
    th { padding: 10px 12px; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--card-border); }
    td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    tr.trace-row { cursor: pointer; transition: background 0.15s ease; }
    tr.trace-row:hover, tr.trace-row.active { background: var(--card-hover); }

    .status-badge {
      display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;
      text-transform: uppercase; font-family: 'JetBrains Mono', monospace;
    }
    .status-success { background: var(--success-bg); color: var(--success); }
    .status-failure { background: var(--critical-bg); color: var(--critical); }

    .severity-badge {
      display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;
      text-transform: uppercase; margin-right: 6px; font-family: 'JetBrains Mono', monospace;
    }
    .badge-critical { background: var(--critical-bg); color: var(--critical); border: 1px solid var(--critical); }
    .badge-warning { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning); }
    .badge-info { background: var(--info-bg); color: var(--info); border: 1px solid var(--info); }

    /* Findings List */
    .finding-item {
      background: rgba(0,0,0,0.2); border-left: 3px solid var(--accent);
      padding: 10px 14px; margin-bottom: 10px; border-radius: 4px; font-size: 0.82rem;
    }
    .finding-critical { border-left-color: var(--critical); }
    .finding-warning { border-left-color: var(--warning); }
    .finding-info { border-left-color: var(--info); }

    /* Span Waterfall / Timeline */
    .span-bar-row { margin-bottom: 12px; }
    .span-bar-info { display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px; }
    .span-bar-track { background: rgba(255,255,255,0.07); height: 10px; border-radius: 5px; overflow: hidden; position: relative; }
    .span-bar-fill { height: 100%; border-radius: 5px; }

    .mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-area">
        <div class="logo-badge">airun</div>
        <div class="header-title">
          <h1>AI Runtime Profiler & Executive Dashboard</h1>
          <p>Inference economics, DAG execution graphs, and diagnostic findings</p>
        </div>
      </div>
      <div class="nav-actions">
        <button class="btn" onclick="fetchSummary(); fetchTraces();">🔄 Refresh</button>
        <button class="btn btn-primary" onclick="alert('Compare feature: Select two trace IDs in the API or run airun compare via CLI.');">⚖️ Compare Runs</button>
      </div>
    </header>

    <!-- Top KPI Cards -->
    <div class="kpi-grid" id="kpi-container">
      <div class="kpi-card">
        <div class="kpi-title">Total Workloads</div>
        <div class="kpi-value" id="kpi-total-traces">...</div>
        <div class="kpi-sub" id="kpi-success-rate">Success Rate: ...</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Total Inference Spend</div>
        <div class="kpi-value" id="kpi-total-cost">...</div>
        <div class="kpi-sub" id="kpi-wasted-cost">Wasted Spend: $0.00</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Total Tokens Analyzed</div>
        <div class="kpi-value" id="kpi-total-tokens">...</div>
        <div class="kpi-sub">Across all LLM steps</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Avg Latency</div>
        <div class="kpi-value" id="kpi-avg-duration">...</div>
        <div class="kpi-sub">Critical path modeled</div>
      </div>
    </div>

    <!-- Main Split: Traces on Left, Detail on Right -->
    <div class="main-split">
      <!-- Left: Recent Execution Traces -->
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title">Recent Execution Workloads</div>
          <span class="mono" style="font-size:0.75rem; color:var(--text-muted);">Local SQLite Store</span>
        </div>
        <div class="table-container">
          <table id="traces-table">
            <thead>
              <tr>
                <th>Workflow Name</th>
                <th>Outcome</th>
                <th>Duration</th>
                <th>Cost</th>
                <th>Tokens</th>
              </tr>
            </thead>
            <tbody id="traces-body">
              <tr><td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted);">Loading traces...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right: Detailed Trace Inspector -->
      <div class="panel" id="detail-panel">
        <div class="panel-header">
          <div class="panel-title">Trace DAG & Diagnostic Intelligence</div>
          <span class="mono" id="detail-trace-id" style="font-size:0.75rem; color:var(--accent);">Select a trace</span>
        </div>

        <div id="detail-content" style="color:var(--text-muted); text-align:center; padding:40px 20px;">
          Select any workload from the left table to inspect its execution hierarchy, critical-path breakdown, and severity-graded findings.
        </div>
      </div>
    </div>
  </div>

  <script>
    let allTraces = [];
    let selectedTraceId = null;

    async function fetchSummary() {
      try {
        const res = await fetch('/api/summary');
        const data = await res.json();
        document.getElementById('kpi-total-traces').innerText = data.total_traces;
        document.getElementById('kpi-success-rate').innerText = `Success Rate: ${data.success_rate}%`;
        document.getElementById('kpi-total-cost').innerText = `$${data.total_cost_usd.toFixed(4)}`;
        document.getElementById('kpi-wasted-cost').innerText = `Wasted Spend: $${data.wasted_cost_usd.toFixed(4)}`;
        document.getElementById('kpi-total-tokens').innerText = Number(data.total_tokens).toLocaleString();
        document.getElementById('kpi-avg-duration').innerText = `${data.avg_duration_ms}ms`;
      } catch (err) {
        console.error("Failed to load summary", err);
      }
    }

    async function fetchTraces() {
      try {
        const res = await fetch('/api/traces?limit=25');
        allTraces = await res.json();
        const tbody = document.getElementById('traces-body');
        tbody.innerHTML = '';

        if (allTraces.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">No traces found. Run python examples/live_multi_model_agent.py to generate some!</td></tr>';
          return;
        }

        allTraces.forEach((t, idx) => {
          const row = document.createElement('tr');
          row.className = 'trace-row' + (idx === 0 ? ' active' : '');
          const isSuccess = String(t.final_status).toLowerCase().includes('success');
          const costStr = t.total_cost_usd ? `$${t.total_cost_usd.toFixed(4)}` : '$0.0000';

          row.innerHTML = `
            <td>
              <div style="font-weight:600; color:#fff;">${t.workflow_name || 'workflow'}</div>
              <div class="mono" style="font-size:0.7rem; color:var(--text-muted);">${t.trace_id.substring(0, 12)}...</div>
            </td>
            <td><span class="status-badge ${isSuccess ? 'status-success' : 'status-failure'}">${isSuccess ? 'SUCCESS' : 'FAILED'}</span></td>
            <td class="mono">${t.duration_ms ? t.duration_ms.toFixed(1) : 0}ms</td>
            <td class="mono" style="color:#60a5fa;">${costStr}</td>
            <td class="mono">${(t.total_tokens || 0).toLocaleString()}</td>
          `;

          row.onclick = () => {
            document.querySelectorAll('.trace-row').forEach(r => r.classList.remove('active'));
            row.classList.add('active');
            loadTraceDetail(t.trace_id);
          };
          tbody.appendChild(row);
        });

        // Automatically load the first trace
        if (allTraces.length > 0) {
          loadTraceDetail(allTraces[0].trace_id);
        }
      } catch (err) {
        console.error("Failed to load traces", err);
      }
    }

    async function loadTraceDetail(traceId) {
      selectedTraceId = traceId;
      document.getElementById('detail-trace-id').innerText = `ID: ${traceId}`;
      const container = document.getElementById('detail-content');
      container.innerHTML = '<div style="text-align:center; padding:30px;">Loading trace detail...</div>';

      try {
        const res = await fetch(`/api/traces/${traceId}`);
        const data = await res.json();

        let findingsHtml = '';
        if (data.findings && data.findings.length > 0) {
          findingsHtml = '<div style="margin-bottom:20px;"><div style="font-weight:600; margin-bottom:10px; font-size:0.9rem;">Diagnostic Findings & Insights:</div>';
          data.findings.forEach(f => {
            const sev = f.severity.toLowerCase();
            const badgeClass = sev === 'critical' ? 'badge-critical' : (sev === 'warning' ? 'badge-warning' : 'badge-info');
            findingsHtml += `
              <div class="finding-item finding-${sev}">
                <span class="severity-badge ${badgeClass}">${f.severity}</span>
                <span>${f.message}</span>
                ${f.suggestion ? `<div style="margin-top:4px; font-size:0.75rem; color:var(--text-muted);">💡 <em>${f.suggestion}</em></div>` : ''}
              </div>
            `;
          });
          findingsHtml += '</div>';
        }

        // Waterfall Spans
        let spansHtml = '<div style="font-weight:600; margin-bottom:12px; font-size:0.9rem;">Execution Span Timeline & Cost Attribution:</div>';
        const maxDuration = data.summary.duration_ms || 1.0;

        data.spans.forEach(s => {
          const dur = s.duration_ms || 0.1;
          const pct = Math.min(100, Math.max(5, (dur / maxDuration) * 100));
          const cost = s.cost_usd ? `$${s.cost_usd.toFixed(4)}` : '$0.00';
          const isLlm = s.kind === 'llm';
          const barColor = isLlm ? '#8b5cf6' : (s.kind === 'tool' ? '#3b82f6' : '#10b981');

          spansHtml += `
            <div class="span-bar-row">
              <div class="span-bar-info">
                <span><strong>[${s.kind}]</strong> ${s.name} ${s.model ? `<span style="color:#a78bfa;">(${s.model})</span>` : ''}</span>
                <span class="mono">${dur.toFixed(1)}ms | ${cost} | ${s.total_tokens || 0} tok</span>
              </div>
              <div class="span-bar-track">
                <div class="span-bar-fill" style="width:${pct}%; background:${barColor};"></div>
              </div>
            </div>
          `;
        });

        // Outcome economics summary box
        const s = data.summary;
        const qualityStr = s.quality_score !== null && s.quality_score !== undefined ? `${(s.quality_score * 100).toFixed(0)}%` : 'N/A';
        const econHtml = `
          <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:14px; margin-bottom:20px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; font-size:0.8rem;">
            <div><span style="color:var(--text-muted);">Critical Path:</span> <strong class="mono">${data.critical_path_ms}ms</strong></div>
            <div><span style="color:var(--text-muted);">Cost/Success:</span> <strong class="mono">$${(s.cost_per_successful_outcome_usd || s.total_cost_usd || 0).toFixed(4)}</strong></div>
            <div><span style="color:var(--text-muted);">Quality Score:</span> <strong class="mono" style="color:#10b981;">${qualityStr}</strong></div>
          </div>
        `;

        container.innerHTML = `
          ${econHtml}
          ${findingsHtml}
          ${spansHtml}
        `;
      } catch (err) {
        container.innerHTML = `<div style="color:var(--critical); padding:20px;">Failed to load trace detail: ${err.message}</div>`;
      }
    }

    // Initialize on load
    fetchSummary();
    fetchTraces();
  </script>
</body>
</html>
"""
