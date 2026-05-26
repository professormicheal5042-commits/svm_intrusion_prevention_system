/**
 * api.js — Centralized API client for SmartGuard IPS
 * ─────────────────────────────────────────────────────────────────────────────
 * Exposes a global `SmartGuardAPI` object consumed by every dashboard page.
 * Plain <script src="../../js/api.js"></script> — no bundler required.
 *
 * Vercel backend: https://svmintrusionpreventionsystem-e9a049kj5.vercel.app
 * Firebase frontend: https://cyber-shield-svm.web.app
 */

(function (global) {
  'use strict';

  // ── Single source of truth for the backend URL ──────────────────────────────
  const BASE_URL = 'https://svmintrusionpreventionsystem.vercel.app';

  // ── Generic fetch wrapper ───────────────────────────────────────────────────
  /**
   * apiFetch(path, opts)
   * Wraps fetch with JSON parsing, error handling, and a timeout.
   * @param {string} path  - e.g. '/api/stats'
   * @param {object} opts  - optional fetch init options
   * @returns {Promise<object>}
   */
  async function apiFetch(path, opts = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 600000); // 60-second timeout

    try {
      const res = await fetch(BASE_URL + path, {
        signal: controller.signal,
        headers: { 'Accept': 'application/json', ...(opts.headers || {}) },
        ...opts,
      });
      clearTimeout(timer);

      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(`[${res.status}] ${path}: ${body}`);
      }
      return await res.json();

    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error(`Timeout fetching ${path}`);
      throw err;
    }
  }

  // ── Public API helpers ──────────────────────────────────────────────────────

  /**
   * GET /api/stats
   */
  async function fetchStats() {
    let user_id = '';
    try { const u = JSON.parse(sessionStorage.getItem('user')); if (u) user_id = '?user_id=' + u.id; } catch (e) { }
    return apiFetch('/api/stats' + user_id);
  }

  /**
   * GET /api/live-traffic
   * Returns: { status, count, data: [ { source_ip, dest_ip, protocol,
   *            prediction, action, timestamp, confidence }, ... ] }
   */
  async function fetchLiveTraffic() {
    return apiFetch('/api/live-traffic');
  }

  /**
   * GET /api/reports
   */
  async function fetchReports() {
    let user_id = '';
    try { const u = JSON.parse(sessionStorage.getItem('user')); if (u) user_id = '?user_id=' + u.id; } catch (e) { }
    return apiFetch('/api/reports' + user_id);
  }

  /**
   * POST /api/upload
   * Sends a multipart/form-data body with the user's file.
   * @param {File} file  - a .csv, .pcap, or .pcapng File object
   * Returns: { status, total_records, threats, accuracy, results: [...] }
   */
  async function uploadFile(file, blockedWebsite) {
    const formData = new FormData();
    formData.append('file', file);
    if (blockedWebsite) {
      formData.append('blocked_website', blockedWebsite);
    }
    // Do NOT set Content-Type header — browser adds it with the multipart boundary
    return apiFetch('/api/upload', { method: 'POST', body: formData, headers: {} });
  }

  // ── Health check ────────────────────────────────────────────────────────────
  /**
   * GET /  — quick ping to check if the Vercel backend is reachable.
   * Returns: { message: "Welcome to the SVM Intrusion Prevention System API" }
   */
  async function ping() {
    return apiFetch('/');
  }

  // ── Save results to database ────────────────────────────────────────────────
  /**
   * POST /api/save
   */
  async function saveResults(results, filename) {
    let user_id = null;
    try { const u = JSON.parse(sessionStorage.getItem('user')); if (u) user_id = u.id; } catch (e) { }

    return apiFetch('/api/save', {
      method: 'POST',
      body: JSON.stringify({ results, filename, user_id }),
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // ── Expose as global object ─────────────────────────────────────────────────
  global.SmartGuardAPI = {
    BASE_URL,
    fetchStats,
    fetchLiveTraffic,
    fetchReports,
    uploadFile,
    saveResults,
    ping,
  };

})(window);
