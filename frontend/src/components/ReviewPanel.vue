<script setup>
import { computed } from "vue";
import { useI18n } from "../i18n/index.js";

const props = defineProps({
  review: { type: Object, required: true },
});

const { t } = useI18n();

const scoreItems = computed(() => {
  const r = props.review;
  return [
    { key: "content", label: t("review.contentMatch"), score: r.content_match?.score ?? 0 },
    { key: "text", label: t("review.textAccuracy"), score: r.text_accuracy?.score ?? 0 },
    { key: "visual", label: t("review.visualCorrectness"), score: r.visual_correctness?.score ?? 0 },
    { key: "quality", label: t("review.overallQuality"), score: r.overall_quality?.score ?? 0 },
  ];
});

const issues = computed(() => {
  const r = props.review;
  return [
    ...(r.content_match?.issues || []),
    ...(r.visual_correctness?.issues || []),
  ];
});

const errors = computed(() => props.review.text_accuracy?.errors || []);
const comments = computed(() => props.review.overall_quality?.comments || []);
</script>

<template>
  <div class="space-y-3 text-sm">
    <p
      class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
      :class="
        review.passed
          ? 'bg-emerald-100 text-emerald-800'
          : 'bg-rose-100 text-rose-800'
      "
    >
      {{ review.passed ? t("review.passed") : t("review.failed") }}
    </p>
    <p v-if="review.summary" class="leading-relaxed text-stone-700">
      {{ review.summary }}
    </p>
    <div class="grid gap-2 sm:grid-cols-2">
      <div v-for="item in scoreItems" :key="item.key">
        <div class="mb-1 flex justify-between text-xs text-stone-500">
          <span>{{ item.label }}</span>
          <span>{{ item.score }}</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-stone-100">
          <div
            class="h-full rounded-full bg-teal-600 transition-all"
            :style="{ width: `${item.score}%` }"
          />
        </div>
      </div>
    </div>
    <div v-if="issues.length" class="rounded-lg bg-stone-50 p-3">
      <p class="mb-1 font-medium text-stone-600">{{ t("review.issuesTitle") }}</p>
      <ul class="list-inside list-disc text-stone-600">
        <li v-for="(x, i) in issues" :key="i">{{ x }}</li>
      </ul>
    </div>
    <div v-if="errors.length" class="rounded-lg bg-stone-50 p-3">
      <p class="mb-1 font-medium text-stone-600">{{ t("review.errorsTitle") }}</p>
      <ul class="list-inside list-disc text-stone-600">
        <li v-for="(x, i) in errors" :key="i">{{ x }}</li>
      </ul>
    </div>
    <div v-if="comments.length" class="rounded-lg bg-stone-50 p-3">
      <p class="mb-1 font-medium text-stone-600">{{ t("review.commentsTitle") }}</p>
      <ul class="list-inside list-disc text-stone-600">
        <li v-for="(x, i) in comments" :key="i">{{ x }}</li>
      </ul>
    </div>
    <ol
      v-if="review.recommendations?.length"
      class="list-decimal space-y-1 pl-5 text-stone-600"
    >
      <li v-for="(r, i) in review.recommendations" :key="i">{{ r }}</li>
    </ol>
    <details class="text-xs text-stone-400">
      <summary class="cursor-pointer">{{ t("review.rawJson") }}</summary>
      <pre class="mt-2 max-h-48 overflow-auto rounded bg-stone-900 p-2 text-stone-100">{{
        JSON.stringify(review, null, 2)
      }}</pre>
    </details>
  </div>
</template>
