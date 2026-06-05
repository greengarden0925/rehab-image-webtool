<script setup>
import { computed, onMounted, ref, watch } from "vue";
import {
  assetUrl,
  createJob,
  fetchExamples,
  fetchJob,
  getApiKey,
  setApiKey,
  subscribeJobEvents,
  validateKey,
} from "./api.js";
import LanguageSwitcher from "./components/LanguageSwitcher.vue";
import LogPanel from "./components/LogPanel.vue";
import StageCard from "./components/StageCard.vue";
import { locale, useI18n } from "./i18n/index.js";

const { t } = useI18n();

const apiKeyInput = ref(getApiKey());
const keyValid = ref(false);
const keyMessage = ref("");
const validating = ref(false);

const prompt = ref("");
const examples = ref([]);
const mode = ref("ab");
const maxIterations = ref(3);

const jobId = ref(null);
const jobStatus = ref(null);
const stages = ref([]);
const logEntries = ref([]);
const resultA = ref(null);
const resultB = ref(null);
const running = ref(false);
const errorMsg = ref("");

const canStart = computed(
  () => keyValid.value && prompt.value.trim().length >= 10 && !running.value
);

function pushLog(entry) {
  logEntries.value = [...logEntries.value, entry];
}

function statusLabel(status) {
  const map = {
    pending: t("status.pending"),
    running: t("status.runningJob"),
    completed: t("status.completed"),
    failed: t("status.failed"),
  };
  return map[status] || status;
}

async function loadExamples() {
  try {
    const data = await fetchExamples(locale.value);
    examples.value = data.examples || [];
  } catch {
    examples.value = [];
  }
}

onMounted(async () => {
  await loadExamples();
  if (apiKeyInput.value) await doValidate(false);
});

watch(locale, async () => {
  await loadExamples();
  keyMessage.value = "";
  if (keyValid.value) keyMessage.value = t("apiKey.valid");
});

async function onLocaleChange() {
  await loadExamples();
}

async function doValidate(showAlert = true) {
  if (!apiKeyInput.value.trim()) {
    keyValid.value = false;
    keyMessage.value = t("apiKey.enterKey");
    return;
  }
  setApiKey(apiKeyInput.value.trim());
  validating.value = true;
  keyMessage.value = "";
  try {
    const res = await validateKey(locale.value);
    keyValid.value = res.valid;
    keyMessage.value =
      res.message || (res.valid ? t("apiKey.valid") : t("apiKey.invalid"));
    if (res.valid) {
      pushLog({ log_message: keyMessage.value, ts: Date.now() / 1000 });
    }
    if (showAlert && !res.valid) errorMsg.value = keyMessage.value;
  } catch {
    keyValid.value = false;
    keyMessage.value = t("apiKey.offline");
  } finally {
    validating.value = false;
  }
}

function loadExample(ex) {
  prompt.value = ex.text;
}

const modeBody = () => {
  if (mode.value === "a") return ["a"];
  if (mode.value === "b") return ["b"];
  return ["a", "b"];
};

async function startJob() {
  errorMsg.value = "";
  running.value = true;
  stages.value = [];
  logEntries.value = [];
  resultA.value = null;
  resultB.value = null;
  jobId.value = null;
  jobStatus.value = "running";

  try {
    const { job_id } = await createJob({
      prompt: prompt.value.trim(),
      modes: modeBody(),
      max_iterations: maxIterations.value,
      locale: locale.value,
    });
    jobId.value = job_id;

    subscribeJobEvents(job_id, (payload) => {
      if (payload.event === "log") {
        pushLog(payload);
      }
      if (payload.event === "stage") {
        stages.value = [...stages.value, payload];
      }
      if (payload.event === "status") {
        jobStatus.value = payload.status;
      }
      if (payload.event === "done") {
        jobStatus.value = payload.status;
        running.value = false;
        if (payload.error) errorMsg.value = payload.error;
        refreshJob();
      }
    });

    const poll = setInterval(async () => {
      if (!running.value) {
        clearInterval(poll);
        return;
      }
      const j = await fetchJob(job_id);
      if (j.status === "completed" || j.status === "failed") {
        running.value = false;
        jobStatus.value = j.status;
        stages.value = j.stages || stages.value;
        if (j.logs?.length) logEntries.value = j.logs;
        resultA.value = j.result_a;
        resultB.value = j.result_b;
        if (j.error) errorMsg.value = j.error;
        clearInterval(poll);
      }
    }, 3000);
  } catch (e) {
    errorMsg.value = e.message || t("errors.generic");
    pushLog({ log_message: errorMsg.value, ts: Date.now() / 1000 });
    running.value = false;
    jobStatus.value = "failed";
  }
}

async function refreshJob() {
  if (!jobId.value) return;
  const j = await fetchJob(jobId.value);
  stages.value = j.stages || [];
  if (j.logs?.length) logEntries.value = j.logs;
  resultA.value = j.result_a;
  resultB.value = j.result_b;
  jobStatus.value = j.status;
}

const bStages = computed(() => stages.value.filter((s) => s.pipeline === "b"));
const aStages = computed(() => stages.value.filter((s) => s.pipeline === "a"));

const finalAUrl = computed(() => {
  if (!jobId.value || !resultA.value) return null;
  return assetUrl(jobId.value, resultA.value.final_image_filename);
});

const finalBUrl = computed(() => {
  if (!jobId.value || !resultB.value) return null;
  return assetUrl(jobId.value, resultB.value.final_image_filename);
});

const bImageVersions = computed(() =>
  bStages.value.filter((s) => s.stage?.startsWith("image_v"))
);

const subtitle = computed(() =>
  t("app.subtitle", {
    a: t("app.aName"),
    b: t("app.bName"),
    apiKey: t("app.apiKeyLink"),
  })
);
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-stone-200 bg-white">
      <div class="mx-auto flex max-w-6xl flex-wrap items-start justify-between gap-4 px-4 py-6">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-stone-900">
            {{ t("app.title") }}
          </h1>
          <p class="mt-1 text-sm text-stone-500">
            {{ subtitle }}
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener"
              class="text-teal-700 underline"
              >{{ t("app.apiKeyLink") }}</a
            >
          </p>
        </div>
        <LanguageSwitcher @change="onLocaleChange" />
      </div>
    </header>

    <main class="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <LogPanel :entries="logEntries" />

      <section class="card">
        <h2 class="mb-3 text-lg font-semibold">{{ t("apiKey.section") }}</h2>
        <p class="mb-3 text-xs text-stone-500">{{ t("apiKey.hint") }}</p>
        <div class="flex flex-wrap gap-2">
          <input
            v-model="apiKeyInput"
            type="password"
            :placeholder="t('apiKey.placeholder')"
            class="min-w-[240px] flex-1 rounded-lg border border-stone-300 px-3 py-2 text-sm"
            @change="keyValid = false"
          />
          <button
            type="button"
            class="btn-secondary"
            :disabled="validating"
            @click="doValidate()"
          >
            {{ validating ? t("apiKey.validating") : t("apiKey.validate") }}
          </button>
        </div>
        <p
          v-if="keyMessage"
          class="mt-2 text-sm"
          :class="keyValid ? 'text-emerald-700' : 'text-rose-600'"
        >
          {{ keyMessage }}
        </p>
      </section>

      <section class="card">
        <h2 class="mb-3 text-lg font-semibold">{{ t("prompt.section") }}</h2>
        <div class="mb-2 flex flex-wrap gap-2">
          <select
            class="rounded-lg border border-stone-300 px-3 py-2 text-sm"
            @change="
              (e) => {
                const ex = examples.find((x) => x.id === e.target.value);
                if (ex) loadExample(ex);
                e.target.value = '';
              }
            "
          >
            <option value="">{{ t("prompt.loadExample") }}</option>
            <option v-for="ex in examples" :key="ex.id" :value="ex.id">
              {{ ex.title }}
            </option>
          </select>
          <span class="self-center text-xs text-stone-400">
            {{ t("prompt.charCount", { count: prompt.length }) }}
          </span>
        </div>
        <textarea
          v-model="prompt"
          rows="12"
          class="w-full rounded-lg border border-stone-300 p-3 font-mono text-sm leading-relaxed"
          :placeholder="t('prompt.placeholder')"
        />
      </section>

      <section class="card">
        <h2 class="mb-3 text-lg font-semibold">{{ t("mode.section") }}</h2>
        <div class="flex flex-wrap gap-4 text-sm">
          <label class="flex items-center gap-2">
            <input v-model="mode" type="radio" value="ab" />
            {{ t("mode.ab") }}
          </label>
          <label class="flex items-center gap-2">
            <input v-model="mode" type="radio" value="a" />
            {{ t("mode.aOnly") }}
          </label>
          <label class="flex items-center gap-2">
            <input v-model="mode" type="radio" value="b" />
            {{ t("mode.bOnly") }}
          </label>
          <label class="flex items-center gap-2">
            {{ t("mode.maxIter") }}
            <select
              v-model.number="maxIterations"
              class="rounded border border-stone-300 px-2 py-1"
            >
              <option :value="1">1</option>
              <option :value="2">2</option>
              <option :value="3">3</option>
            </select>
          </label>
        </div>
        <p class="mt-2 text-xs text-stone-500">{{ t("mode.costHint") }}</p>
        <button
          type="button"
          class="btn-primary mt-4"
          :disabled="!canStart"
          @click="startJob"
        >
          {{ running ? t("mode.running") : t("mode.start") }}
        </button>
        <p v-if="errorMsg" class="mt-2 text-sm text-rose-600">{{ errorMsg }}</p>
      </section>

      <section
        v-if="finalAUrl || finalBUrl"
        class="card bg-gradient-to-br from-white to-stone-50"
      >
        <h2 class="mb-4 text-lg font-semibold">{{ t("compare.section") }}</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <div v-if="finalAUrl">
            <h3 class="mb-2 text-sm font-bold text-amber-800">{{ t("compare.aTitle") }}</h3>
            <img
              :src="finalAUrl"
              alt="A"
              class="w-full rounded-lg border border-amber-200 bg-white object-contain"
            />
            <p v-if="resultA" class="mt-2 text-xs text-stone-500">
              {{ t("stageDetail.aResultNote") }}
            </p>
          </div>
          <div v-if="finalBUrl">
            <h3 class="mb-2 text-sm font-bold text-teal-800">{{ t("compare.bTitle") }}</h3>
            <img
              :src="finalBUrl"
              alt="B"
              class="w-full rounded-lg border border-teal-200 bg-white object-contain"
            />
          </div>
        </div>
        <div v-if="bImageVersions.length" class="mt-4">
          <p class="mb-2 text-xs font-medium text-stone-500">{{ t("compare.bThumbs") }}</p>
          <div class="flex flex-wrap gap-2">
            <a
              v-for="(s, i) in bImageVersions"
              :key="i"
              :href="s.data?.image_url || assetUrl(jobId, s.data?.filename)"
              target="_blank"
              class="block h-20 w-20 overflow-hidden rounded border border-stone-200"
            >
              <img
                :src="s.data?.image_url || assetUrl(jobId, s.data?.filename)"
                class="h-full w-full object-cover"
                alt=""
              />
            </a>
          </div>
        </div>
      </section>

      <section v-if="aStages.length" class="space-y-3">
        <h2 class="text-lg font-semibold text-amber-900">{{ t("timeline.a") }}</h2>
        <StageCard
          v-for="(s, i) in aStages"
          :key="'a-' + i"
          :stage="s"
          :job-id="jobId"
        />
      </section>

      <section v-if="bStages.length" class="space-y-3">
        <h2 class="text-lg font-semibold text-teal-900">{{ t("timeline.b") }}</h2>
        <StageCard
          v-for="(s, i) in bStages"
          :key="'b-' + i"
          :stage="s"
          :job-id="jobId"
        />
      </section>

      <p v-if="running" class="animate-pulse text-center text-sm text-stone-500">
        {{ t("status.running", { status: statusLabel(jobStatus) }) }}
      </p>
    </main>
  </div>
</template>
