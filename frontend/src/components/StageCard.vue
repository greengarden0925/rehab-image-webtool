<script setup>
import { computed } from "vue";
import { useI18n } from "../i18n/index.js";
import ReviewPanel from "./ReviewPanel.vue";

const props = defineProps({
  stage: { type: Object, required: true },
  jobId: { type: String, default: "" },
});

const { t } = useI18n();

const stageTitle = computed(() => {
  const key = `stages.${props.stage.stage}`;
  const label = t(key);
  return label === key ? props.stage.stage || t("stages.step") : label;
});

const imageUrl = computed(() => {
  const d = props.stage.data || {};
  if (d.image_url) return d.image_url;
  const fn = d.filename || d.image_filename || d.final_image_filename;
  if (fn && props.jobId) return `/api/jobs/${props.jobId}/assets/${fn}`;
  return null;
});

const isReview = computed(() => props.stage.stage?.startsWith("review_"));
const showPrompt = computed(
  () => props.stage.stage === "prompt_generated" && props.stage.data?.text
);
const showFeedback = computed(
  () => props.stage.stage === "refine_start" && props.stage.data?.feedback
);
</script>

<template>
  <article
    class="card border-l-4"
    :class="stage.pipeline === 'a' ? 'border-l-amber-500' : 'border-l-teal-600'"
  >
    <header class="mb-3 flex flex-wrap items-center gap-2">
      <span
        class="rounded px-2 py-0.5 text-xs font-bold uppercase"
        :class="
          stage.pipeline === 'a'
            ? 'bg-amber-100 text-amber-900'
            : 'bg-teal-100 text-teal-900'
        "
      >
        {{ stage.pipeline === "a" ? "A" : "B" }}
      </span>
      <h3 class="font-semibold text-stone-800">{{ stageTitle }}</h3>
      <span v-if="stage.elapsed_ms" class="text-xs text-stone-400">
        {{ (stage.elapsed_ms / 1000).toFixed(1) }}s
      </span>
    </header>

    <img
      v-if="imageUrl"
      :src="imageUrl"
      alt=""
      class="mb-3 max-h-96 w-full rounded-lg border border-stone-200 object-contain bg-stone-100"
    />

    <details v-if="showPrompt" class="mb-3">
      <summary class="cursor-pointer text-sm font-medium text-teal-800">
        {{ t("stageDetail.promptSummary") }}
      </summary>
      <pre
        class="mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-stone-50 p-3 text-xs text-stone-700"
        >{{ stage.data.text }}</pre
      >
    </details>

    <div
      v-if="showFeedback"
      class="mb-3 rounded-lg bg-amber-50 p-3 text-sm text-stone-700"
    >
      <p class="mb-1 font-medium text-amber-900">{{ t("stageDetail.refineTitle") }}</p>
      <pre class="whitespace-pre-wrap text-xs">{{ stage.data.feedback }}</pre>
    </div>

    <ReviewPanel v-if="isReview" :review="stage.data" />

    <p v-if="stage.stage === 'finished'" class="text-sm text-stone-600">
      {{
        t("stageDetail.finishedMeta", {
          file: stage.data.final_image_filename,
          passed: stage.data.final_passed
            ? t("stageDetail.passed")
            : t("stageDetail.notPassed"),
          iter: stage.data.total_iterations,
          sec: stage.data.duration_sec,
        })
      }}
    </p>

    <p v-if="stage.stage === 'image_raw'" class="text-xs text-stone-500">
      {{ t("stageDetail.aNote", { sec: stage.data.duration_sec }) }}
    </p>
  </article>
</template>
