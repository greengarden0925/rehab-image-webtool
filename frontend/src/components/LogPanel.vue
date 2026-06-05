<script setup>
import { nextTick, ref, watch } from "vue";
import { useI18n } from "../i18n/index.js";

const props = defineProps({
  entries: { type: Array, default: () => [] },
});

const { t } = useI18n();
const box = ref(null);

watch(
  () => props.entries.length,
  async () => {
    await nextTick();
    if (box.value) box.value.scrollTop = box.value.scrollHeight;
  }
);

function formatTime(ts) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString();
}
</script>

<template>
  <section class="card">
    <div class="mb-2 flex items-center justify-between">
      <h2 class="text-lg font-semibold">{{ t("log.title") }}</h2>
    </div>
    <div
      ref="box"
      class="h-48 overflow-y-auto rounded-lg border border-stone-200 bg-stone-900 p-3 font-mono text-xs leading-relaxed text-stone-100"
    >
      <p v-if="!entries.length" class="text-stone-400">{{ t("log.empty") }}</p>
      <div v-for="(e, i) in entries" :key="i" class="mb-1.5">
        <span class="text-stone-500">[{{ formatTime(e.ts) }}]</span>
        {{ e.log_message || e.message }}
      </div>
    </div>
  </section>
</template>
