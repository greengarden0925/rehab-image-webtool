const KEY_STORAGE = "gemini_api_key";
const LOCALE_STORAGE = "webtool_locale";

export function getApiKey() {
  return sessionStorage.getItem(KEY_STORAGE) || "";
}

export function setApiKey(key) {
  sessionStorage.setItem(KEY_STORAGE, key);
}

export function getLocale() {
  return sessionStorage.getItem(LOCALE_STORAGE) === "en" ? "en" : "zh-TW";
}

export function apiHeaders() {
  const key = getApiKey();
  return {
    "Content-Type": "application/json",
    ...(key ? { "X-Gemini-Api-Key": key } : {}),
  };
}

export async function validateKey(locale = getLocale()) {
  const res = await fetch(`/api/validate-key?locale=${encodeURIComponent(locale)}`, {
    method: "POST",
    headers: apiHeaders(),
  });
  return res.json();
}

export async function fetchExamples(locale = getLocale()) {
  const res = await fetch(`/api/examples?locale=${encodeURIComponent(locale)}`);
  return res.json();
}

export async function createJob(body) {
  const res = await fetch("/api/jobs", {
    method: "POST",
    headers: apiHeaders(),
    body: JSON.stringify({ ...body, locale: body.locale || getLocale() }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : res.statusText;
    throw new Error(msg);
  }
  return res.json();
}

export async function fetchJob(jobId) {
  const res = await fetch(`/api/jobs/${jobId}`);
  return res.json();
}

export function assetUrl(jobId, filename) {
  if (!filename) return null;
  return `/api/jobs/${jobId}/assets/${encodeURIComponent(filename)}`;
}

export function subscribeJobEvents(jobId, onMessage) {
  const es = new EventSource(`/api/jobs/${jobId}/events`);
  es.onmessage = (e) => {
    try {
      onMessage(JSON.parse(e.data));
    } catch {
      /* ignore */
    }
  };
  es.onerror = () => es.close();
  return es;
}
