import { InteractionRequiredAuthError, PublicClientApplication } from "@azure/msal-browser";
import "../styles.css";

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
    redirectUri: window.location.origin,
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

function renderIdentity() {
  identityStatus.textContent = account ? `Signed in as ${account.username}` : "Not signed in";
  signInButton.hidden = Boolean(account);
  signOutButton.hidden = !account;
}

async function signIn() {
  const response = await auth.loginPopup({ scopes: [deployment.apiScope] });
  account = response.account;
  auth.setActiveAccount(account);
  renderIdentity();
  return account;
}

async function accessToken() {
  account ??= auth.getActiveAccount() ?? auth.getAllAccounts()[0] ?? null;
  if (!account) await signIn();
  try {
    return (await auth.acquireTokenSilent({ account, scopes: [deployment.apiScope] })).accessToken;
  } catch (error) {
    if (!(error instanceof InteractionRequiredAuthError)) throw error;
    return (await auth.acquireTokenPopup({ account, scopes: [deployment.apiScope] })).accessToken;
  }
}

signInButton.addEventListener("click", async () => {
  try { await signIn(); } catch (error) { identityStatus.textContent = `Sign-in failed: ${error.message}`; }
});
signOutButton.addEventListener("click", async () => {
  await auth.logoutPopup({ account });
  account = null;
  renderIdentity();
});

document.querySelector("#as-of").value = new Date().toISOString().slice(0, 10);
renderIdentity();

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = false;
  askButton.disabled = true;
  document.querySelector("#status").textContent = "Retrieving authorised policy evidence…";
  document.querySelector("#answer").textContent = "";
  document.querySelector("#citations").replaceChildren();
  try {
    const response = await fetch(`${deployment.apiBaseUrl}/ask`, {
      method: "POST",
      headers: { Authorization: `Bearer ${await accessToken()}`, "Content-Type": "application/json" },
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
