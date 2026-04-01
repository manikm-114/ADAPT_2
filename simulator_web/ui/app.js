const figureEl = document.getElementById("figure");
const generateBtn = document.getElementById("generateBtn");
const statusEl = document.getElementById("status");
const imgEl = document.getElementById("figureImg");
const cfgEl = document.getElementById("cfg");
const logEl = document.getElementById("log");
const figureOverviewEl = document.getElementById("figureOverview");

const groupEls = {
  load: document.getElementById("group_load"),
  review: document.getElementById("group_review"),
  policy: document.getElementById("group_policy"),
  collusion: document.getElementById("group_collusion"),
  longterm: document.getElementById("group_longterm")
};

let FIG_META = [];

const PARAMS = {
  fig2_baseline: {
    load: [["run.seed", "123"], ["sim.T", "20"], ["submissions.mean_per_timestep", "30"], ["capacity.max_reviews_per_timestep", "180"]],
    review: [["submissions.quality_mean", "0.60"], ["review_process.ai_fraction_target", "0.20"]],
    policy: [["triage.threshold", "0.45"], ["governance.backlog_high", "40"], ["governance.backlog_low", "10"], ["governance.ai_step", "0.05"], ["governance.triage_step", "0.02"]],
    collusion: [], longterm: []
  },
  fig3_submission_surge: {
    load: [["run.seed", "123"], ["sim.T", "30"], ["submissions.mean_per_timestep", "30"], ["capacity.max_reviews_per_timestep", "45"], ["scenario.submission_surge.start_t", "5"], ["scenario.submission_surge.end_t", "12"], ["scenario.submission_surge.mean_per_timestep", "90"]],
    review: [["review_process.ai_fraction_target", "0.20"]],
    policy: [["triage.threshold", "0.45"], ["governance.backlog_high", "40"], ["governance.backlog_low", "15"], ["governance.ai_min", "0.13"], ["governance.ai_step", "0.03"], ["governance.triage_step", "0.03"]],
    collusion: [], longterm: []
  },
  fig4_quality_drift: {
    load: [["run.seed", "123"], ["sim.T", "20"], ["submissions.mean_per_timestep", "30"]],
    review: [["submissions.quality_mean", "0.60"], ["review_process.ai_fraction_target", "0.10"]],
    policy: [["triage.threshold", "0.45"], ["governance.backlog_high", "80"], ["governance.backlog_low", "20"], ["governance.ai_max", "0.20"], ["governance.ai_step", "0.025"], ["governance.triage_step", "0.02"], ["governance.triage_max", "0.65"]],
    collusion: [], longterm: []
  },
  fig5_disagreement_spike: {
    load: [["run.seed", "123"], ["sim.T", "30"], ["submissions.mean_per_timestep", "30"]],
    review: [["submissions.quality_mean", "0.60"], ["review_process.ai_fraction_target", "0.10"], ["scenario.disagreement_spike.start_t", "12"], ["scenario.disagreement_spike.end_t", "22"], ["scenario.disagreement_spike.noise_multiplier", "3.0"]],
    policy: [["triage.threshold", "0.45"], ["governance.backlog_high", "25"], ["governance.backlog_low", "8"], ["governance.ai_step", "0.05"], ["governance.triage_step", "0.03"], ["governance.triage_max", "0.70"]],
    collusion: [], longterm: []
  },
  fig6_disagreement: {
    load: [["run.seed", "123"], ["sim.T", "20"], ["submissions.mean_per_timestep", "25"], ["capacity.max_reviews_per_timestep", "180"]],
    review: [["review_process.ai_fraction_target", "0.10"], ["review_process.disagreement_threshold", "1.0"], ["scenario.disagreement_spike.start_t", "10"], ["scenario.disagreement_spike.end_t", "16"], ["scenario.disagreement_spike.noise_multiplier", "2.2"]],
    policy: [["triage.threshold", "0.45"], ["governance.backlog_high", "40"], ["governance.backlog_low", "10"], ["governance.ai_max", "0.25"], ["governance.ai_step", "0.02"], ["governance.triage_max", "0.60"], ["governance.recovery_steps", "4"]],
    collusion: [], longterm: []
  },
  fig7_postpub_credit: {
    load: [["run.seed", "123"], ["sim.T", "80"]],
    review: [],
    policy: [],
    collusion: [],
    longterm: [["authors.high_quality_base_impact", "6.0"], ["authors.low_quality_base_impact", "2.0"], ["authors.impact_drift_per_t", "0.03"], ["authors.impact_noise_std", "0.25"], ["authors.expected_impact", "3.5"], ["authors.alpha", "0.08"], ["reviewers.insightful_alignment", "0.85"], ["reviewers.noisy_alignment", "0.35"], ["reviewers.noise_std", "0.08"], ["reviewers.alpha", "0.06"]]
  },
  fig8_longterm: {
    load: [["run.seed", "123"], ["sim.T", "120"]],
    review: [],
    policy: [["governance.ai_min", "0.15"], ["governance.ai_max", "0.30"], ["governance.triage_min", "0.40"], ["governance.triage_max", "0.70"], ["governance.triage_step", "0.006"], ["governance.inertia", "0.92"]],
    collusion: [],
    longterm: [["postpub_signal.base", "0.20"], ["postpub_signal.drift_per_t", "0.003"], ["postpub_signal.noise_std", "0.02"], ["postpub_signal.lag_alpha", "0.05"], ["objectives.quality_base", "0.60"], ["objectives.trust_base", "0.65"]]
  },
  collusion_enabled: {
    load: [["run.seed", "123"], ["sim.T", "30"], ["submissions.mean_per_timestep", "30"]],
    review: [],
    policy: [["triage.threshold", "0.45"], ["governance.ai_step", "0.05"], ["governance.triage_step", "0.03"]],
    collusion: [["scenario.collusion_attack.start_t", "6"], ["scenario.collusion_attack.threshold", "0.24"], ["scenario.collusion_attack.patience", "1"], ["scenario.collusion_attack.within_cluster_target", "0.28"], ["scenario.collusion_attack.noise_std", "0.03"], ["scenario.collusion_attack.mitigation_strength", "0.35"], ["scenario.collusion_attack.ema_alpha", "0.30"], ["scenario.collusion_attack.max_share", "0.35"]],
    longterm: []
  },
  collusion_disabled: {
    load: [["run.seed", "123"], ["sim.T", "30"], ["submissions.mean_per_timestep", "30"]],
    review: [],
    policy: [["triage.threshold", "0.45"], ["governance.ai_step", "0.05"], ["governance.triage_step", "0.03"], ["governance.disable_capture_mitigation", "true"]],
    collusion: [["scenario.collusion_attack.start_t", "6"], ["scenario.collusion_attack.threshold", "0.24"], ["scenario.collusion_attack.patience", "1"], ["scenario.collusion_attack.within_cluster_target", "0.28"], ["scenario.collusion_attack.noise_std", "0.03"], ["scenario.collusion_attack.mitigation_strength", "0.35"], ["scenario.collusion_attack.ema_alpha", "0.30"], ["scenario.collusion_attack.max_share", "0.35"]],
    longterm: []
  }
};

function fillList(id, items) {
  const el = document.getElementById(id);
  el.innerHTML = "";
  items.forEach(x => {
    const li = document.createElement("li");
    li.textContent = x;
    el.appendChild(li);
  });
}

function makeParamInput(key, value) {
  const div = document.createElement("div");
  div.className = "param";
  div.innerHTML = `<label>${key}<input data-key="${key}" value="${value}"></label>`;
  return div;
}

function renderGroup(groupName, items) {
  const el = groupEls[groupName];
  el.innerHTML = "";
  items.forEach(([key, value]) => el.appendChild(makeParamInput(key, value)));
}

function renderParamInputs() {
  const fig = figureEl.value;
  const groups = PARAMS[fig] || {load:[], review:[], policy:[], collusion:[], longterm:[]};
  renderGroup("load", groups.load || []);
  renderGroup("review", groups.review || []);
  renderGroup("policy", groups.policy || []);
  renderGroup("collusion", groups.collusion || []);
  renderGroup("longterm", groups.longterm || []);

  const meta = FIG_META.find(x => x.id === fig);
  figureOverviewEl.textContent = meta ? meta.overview : "";
}

async function loadMeta() {
  const res = await fetch("/api/meta");
  const data = await res.json();

  FIG_META = data.figures || [];
  FIG_META.forEach(f => {
    const opt = document.createElement("option");
    opt.value = f.id;
    opt.textContent = f.label;
    figureEl.appendChild(opt);
  });

  fillList("agentsList", data.model_overview.agents || []);
  fillList("paperVarsList", data.model_overview.paper_variables || []);
  fillList("signalsList", data.model_overview.observed_signals || []);
  fillList("controlsList", data.model_overview.policy_controls || []);
  fillList("assumptionsList", data.model_overview.assumptions || []);

  renderParamInputs();
}

function collectParams() {
  const params = {};
  document.querySelectorAll("input[data-key]").forEach(el => {
    params[el.dataset.key] = el.value;
  });
  return params;
}

async function generate() {
  statusEl.textContent = "Generating...";
  imgEl.style.display = "none";
  cfgEl.textContent = "";
  logEl.textContent = "";

  const body = { figure_id: figureEl.value, params: collectParams() };

  const res = await fetch("/api/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });

  const data = await res.json();

  if (!res.ok || !data.ok) {
    statusEl.textContent = "Failed.";
    logEl.textContent = data.error || JSON.stringify(data, null, 2);
    return;
  }

  statusEl.textContent = `Done: ${data.figure_label}`;
  imgEl.src = "/api/image?path=" + encodeURIComponent(data.image_path) + "&ts=" + Date.now();
  imgEl.style.display = "block";
  cfgEl.textContent = JSON.stringify(data.used_config, null, 2);
  logEl.textContent = data.log || "";
}

figureEl.addEventListener("change", renderParamInputs);
generateBtn.addEventListener("click", generate);

loadMeta();
