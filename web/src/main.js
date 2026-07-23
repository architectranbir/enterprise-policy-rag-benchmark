import { InteractionRequiredAuthError, PublicClientApplication } from "@azure/msal-browser";
import "../styles.css";
import { casesToCsv, download, metric, milliseconds } from "./benchmark.js";

const deployment = {
  tenantId: import.meta.env.VITE_ENTRA_TENANT_ID,
  clientId: import.meta.env.VITE_ENTRA_WEB_CLIENT_ID,
  apiScope: import.meta.env.VITE_ENTRA_API_SCOPE,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
};
const missing = Object.entries(deployment).filter(([, value]) => !value).map(([name]) => name);
if (missing.length) throw new Error(`Web deployment configuration is missing: ${missing.join(", ")}`);

const auth = new PublicClientApplication({
  auth: {
    clientId: deployment.clientId,
    authority: `https://login.microsoftonline.com/${deployment.tenantId}`,
    redirectUri: `${window.location.origin}/`,
    postLogoutRedirectUri: `${window.location.origin}/`,
  },
  cache: { cacheLocation: "sessionStorage" },
});

const identityStatus = document.querySelector("#identity-status");
const signInButton = document.querySelector("#sign-in");
const signOutButton = document.querySelector("#sign-out");
const askButton = document.querySelector("#ask");
const form = document.querySelector("#ask-form");
const result = document.querySelector("#result");

await auth.initialize();
const redirectResult = await auth.handleRedirectPromise();
let account = redirectResult?.account ?? auth.getAllAccounts()[0] ?? null;
if (account) auth.setActiveAccount(account);

function renderIdentity() {
  identityStatus.textContent = account ? `Signed in as ${account.username}` : "Not signed in";
  signInButton.hidden = Boolean(account);
  signOutButton.hidden = !account;
}

async function signIn() {
  identityStatus.textContent = "Redirecting to Microsoft sign-in…";
  await auth.loginRedirect({ scopes: [deployment.apiScope] });
}

async function accessToken() {
  account ??= auth.getActiveAccount() ?? auth.getAllAccounts()[0] ?? null;
  if (!account) {
    await signIn();
    return null;
  }
  try {
    return (await auth.acquireTokenSilent({ account, scopes: [deployment.apiScope] })).accessToken;
  } catch (error) {
    if (!(error instanceof InteractionRequiredAuthError)) throw error;
    await auth.acquireTokenRedirect({ account, scopes: [deployment.apiScope] });
    return null;
  }
}

signInButton.addEventListener("click", async () => {
  try { await signIn(); } catch (error) { identityStatus.textContent = `Sign-in failed: ${error.message}`; }
});
signOutButton.addEventListener("click", async () => {
  await auth.logoutRedirect({ account });
});

document.querySelector("#as-of").value = new Date().toISOString().slice(0, 10);
renderIdentity();

for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item === tab));
    document.querySelectorAll(".panel").forEach((panel) => { panel.hidden = panel.id !== tab.dataset.panel; });
    if (tab.dataset.panel === "benchmark-panel") loadRuns();
  });
}

let selectedRun = null;
function bar(label, value, maximum = 1) {
  const percent = value == null ? 0 : (maximum ? Math.min(100, (value / maximum) * 100) : 0);
  return `<div class="bar-row"><span>${label}</span><div class="bar-track"><div class="bar" style="width:${percent}%"></div></div><strong>${maximum === 1 ? metric(value) : milliseconds(value)}</strong></div>`;
}
function renderRuns(runs) {
  document.querySelector("#benchmark-empty").hidden = runs.length > 0;
  document.querySelector("#benchmark-content").hidden = runs.length === 0;
  if (!runs.length) return;
  document.querySelector("#comparison-cards").innerHTML = runs.map((run) => run.recall_at_k == null
    ? `<article class="metric-card"><h3>${run.backend}</h3><p class="muted">${run.mode}</p><p class="metric">Pass ${metric(run.pass_rate)}</p><p>ACL ${metric(run.acl_isolation_rate)} · Refusal ${metric(run.refusal_accuracy)}</p><p>Citations ${metric(run.citation_correctness)} · Grounded ${metric(run.groundedness)}</p></article>`
    : `<article class="metric-card"><h3>${run.backend}</h3><p class="muted">${run.mode}</p><p class="metric">Recall ${metric(run.recall_at_k)}</p><p>MRR ${metric(run.mrr)} · nDCG ${metric(run.ndcg_at_k)}</p><p>p50 ${milliseconds(run.p50_latency_ms)} · p95 ${milliseconds(run.p95_latency_ms)}</p></article>`).join("");
  const retrievalRuns = runs.filter((run) => run.recall_at_k != null);
  document.querySelector("#quality-chart").innerHTML = retrievalRuns.map((run) => bar(`${run.mode}: ${run.backend}`, run.recall_at_k)).join("");
  const maximum = Math.max(...retrievalRuns.map((run) => run.p95_latency_ms ?? 0), 1);
  document.querySelector("#latency-chart").innerHTML = retrievalRuns.map((run) => bar(`${run.mode}: ${run.backend}`, run.p95_latency_ms, maximum)).join("");
  document.querySelector("#run-history").innerHTML = runs.map((run) => `<tr><td>${run.backend}</td><td>${run.mode}</td><td>${run.dataset}</td><td>${metric(run.recall_at_k)}</td><td>${metric(run.mrr)}</td><td>${metric(run.ndcg_at_k)}</td><td>${milliseconds(run.p50_latency_ms)}</td><td>${milliseconds(run.p95_latency_ms)}</td><td><button type="button" data-run-id="${run.run_id}">View</button></td></tr>`).join("");
  document.querySelectorAll("[data-run-id]").forEach((button) => button.addEventListener("click", () => loadRun(button.dataset.runId)));
}
async function loadRuns() {
  try {
    const response = await fetch(`${deployment.apiBaseUrl}/benchmarks/runs`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderRuns(await response.json());
  } catch (error) { document.querySelector("#benchmark-progress").textContent = `History unavailable: ${error.message}`; renderRuns([]); }
}
async function loadRun(runId) {
  const response = await fetch(`${deployment.apiBaseUrl}/benchmarks/runs/${encodeURIComponent(runId)}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  selectedRun = await response.json();
  document.querySelector("#run-detail").hidden = false;
  document.querySelector("#case-history").innerHTML = selectedRun.cases.map((item) => `<tr><td>${item.case_id}</td><td>${item.repetition || 1}</td><td>${(item.retrieved_chunk_ids || item.returned_chunk_ids || []).join("<br>")}</td><td>${item.control ? (item.passed ? "Pass" : "Fail") : metric(item.recall_at_k)}</td><td>${item.control ? metric(item.citation_correct) : metric(item.reciprocal_rank)}</td><td>${item.control ? metric(item.grounded) : metric(item.ndcg_at_k)}</td><td>${milliseconds(item.latency_ms)}</td></tr>`).join("");
}
document.querySelector("#refresh-runs").addEventListener("click", loadRuns);
document.querySelector("#benchmark-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = document.querySelector("#benchmark-progress");
  status.textContent = "Requesting secured benchmark job…";
  const response = await fetch(`${deployment.apiBaseUrl}/benchmarks/runs`, { method: "POST" });
  const data = await response.json().catch(() => ({}));
  status.textContent = response.ok ? "Benchmark accepted. Refresh history to monitor progress." : (data.detail || "Benchmark job is not configured.");
});
document.querySelector("#export-json").addEventListener("click", () => selectedRun && download(`${selectedRun.backend}.json`, JSON.stringify(selectedRun, null, 2), "application/json"));
document.querySelector("#export-csv").addEventListener("click", () => selectedRun && download(`${selectedRun.backend}.csv`, casesToCsv(selectedRun.cases), "text/csv"));

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = false;
  askButton.disabled = true;
  document.querySelector("#status").textContent = "Retrieving authorised policy evidence…";
  document.querySelector("#answer").textContent = "";
  document.querySelector("#citations").replaceChildren();
  try {
    const token = await accessToken();
    if (!token) return;
    const response = await fetch(`${deployment.apiBaseUrl}/ask`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        question: document.querySelector("#question").value,
        as_of: document.querySelector("#as-of").value,
        top_k: 5,
      }),
    });
    const data = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
    if (!response.ok) throw new Error(data.detail || "Request failed");
    document.querySelector("#status").textContent = `Backend: ${data.backend} · Correlation: ${data.correlation_id}`;
    document.querySelector("#answer").textContent = data.answer;
    for (const citation of data.citations) {
      const item = document.createElement("li");
      item.textContent = `${citation.document_title} v${citation.version}, section ${citation.section_number} (${citation.chunk_id})`;
      document.querySelector("#citations").append(item);
    }
  } catch (error) {
    document.querySelector("#status").textContent = "Request failed";
    document.querySelector("#answer").textContent = error.message;
  } finally {
    askButton.disabled = false;
  }
});
