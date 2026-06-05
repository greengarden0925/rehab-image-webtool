import { computed, ref } from "vue";
import en from "./en.js";
import zhTW from "./zh-TW.js";

const STORAGE_KEY = "webtool_locale";
const messages = { "zh-TW": zhTW, en };

export const locale = ref(
  sessionStorage.getItem(STORAGE_KEY) === "en" ? "en" : "zh-TW"
);

export function setLocale(loc) {
  locale.value = loc === "en" ? "en" : "zh-TW";
  sessionStorage.setItem(STORAGE_KEY, locale.value);
}

function get(obj, path) {
  return path.split(".").reduce((o, k) => (o ? o[k] : undefined), obj);
}

function interpolate(str, params = {}) {
  if (!str || typeof str !== "string") return str;
  return str.replace(/\{(\w+)\}/g, (_, k) =>
    params[k] !== undefined ? String(params[k]) : `{${k}}`
  );
}

export function useI18n() {
  const t = (key, params) => {
    const pack = messages[locale.value] || messages["zh-TW"];
    const val = get(pack, key) ?? get(messages["zh-TW"], key) ?? key;
    return interpolate(val, params);
  };

  const localeLabel = computed(() =>
    locale.value === "en" ? "English" : "繁體中文"
  );

  return { t, locale, setLocale, localeLabel };
}
