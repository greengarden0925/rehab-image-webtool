<script setup>
import { useI18n } from "../i18n/index.js";

const { t, locale, setLocale } = useI18n();
const emit = defineEmits(["change"]);

function onChange(e) {
  setLocale(e.target.value);
  emit("change", locale.value);
}
</script>

<template>
  <label class="flex items-center gap-2 text-sm text-stone-600">
    <span class="font-medium">{{ t("lang.label") }}</span>
    <select
      :value="locale"
      class="rounded-lg border border-stone-300 bg-white px-3 py-1.5 text-sm"
      @change="onChange"
    >
      <option value="zh-TW">{{ t("lang.zhTW") }}</option>
      <option value="en">{{ t("lang.en") }}</option>
    </select>
  </label>
</template>
