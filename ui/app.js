const API = "http://127.0.0.1:8000";

let currentDecisionId = null;
function setFeedbackEnabled(enabled) {
  document.querySelector(".good").disabled = !enabled;
  document.querySelector(".bad").disabled = !enabled;
}

/* ---------------- DRIVERS ---------------- */

const drivers = [
  { id: "VER", name: "Max Verstappen", color: "#1e41ff" },
  { id: "PER", name: "Sergio Perez", color: "#1e41ff" },

  { id: "HAM", name: "Lewis Hamilton", color: "#00d2be" },
  { id: "RUS", name: "George Russell", color: "#00d2be" },

  { id: "LEC", name: "Charles Leclerc", color: "#dc0000" },
  { id: "SAI", name: "Carlos Sainz", color: "#dc0000" },

  { id: "NOR", name: "Lando Norris", color: "#ff8700" },
  { id: "PIA", name: "Oscar Piastri", color: "#ff8700" },

  { id: "ALO", name: "Fernando Alonso", color: "#006f62" },
  { id: "STR", name: "Lance Stroll", color: "#006f62" },

  { id: "OCO", name: "Esteban Ocon", color: "#0090ff" },
  { id: "GAS", name: "Pierre Gasly", color: "#0090ff" },

  { id: "ALB", name: "Alexander Albon", color: "#005aff" },
  { id: "SAR", name: "Logan Sargeant", color: "#005aff" },

  { id: "BOT", name: "Valtteri Bottas", color: "#900000" },
  { id: "ZHO", name: "Zhou Guanyu", color: "#900000" },

  { id: "MAG", name: "Kevin Magnussen", color: "#b6babd" },
  { id: "HUL", name: "Nico Hulkenberg", color: "#b6babd" },

  { id: "TSU", name: "Yuki Tsunoda", color: "#2b4562" },
  { id: "RIC", name: "Daniel Ricciardo", color: "#2b4562" },
];

document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("userSelect");
  setFeedbackEnabled(false);

  drivers.forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d.id;
    opt.textContent = d.name;
    opt.style.color = d.color;
    sel.appendChild(opt);
  });

  sel.value = drivers[0].id;
  updateTyreColor();

  loadLearningChartForDriver(sel.value);

  sel.addEventListener("change", () => {
    loadLearningChartForDriver(sel.value);
  });
});

/* ---------------- TYRES ---------------- */

function updateTyreColor() {
  const tyre = document.getElementById("tyre");
  const value = tyre.value;

  tyre.style.fontWeight = "bold";

  if (value === "SOFT") tyre.style.color = "#ff2a2a";
  if (value === "MEDIUM") tyre.style.color = "#ffd000";
  if (value === "HARD") tyre.style.color = "#ffffff";
}

/* ---------------- LAP SEND ---------------- */

async function sendLap() {
  currentDecisionId = null;
  setFeedbackEnabled(false);
  if (
    !userSelect.value ||
    !lap.value ||
    !position.value ||
    !tyre.value ||
    !tyreLife.value ||
    !lapTime.value
  ) {
    alert("Please fill in all telemetry fields before sending.");
    return;
  }
  updateTyreColor();

  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("decisionText").innerText = "";

  const wear = Math.min(100, tyreLife.value * 5);
  document.getElementById("tyreFill").style.width = `${wear}%`;

  const payload = {
    userId: userSelect.value,
    lap: lap.value,
    position: position.value,
    tyre: tyre.value,
    tyre_life: tyreLife.value,
    lap_time_sec: lapTime.value,
  };

  const res = await fetch(`${API}/api/laps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    document.getElementById("loader").classList.add("hidden");
    alert("Decision engine failed");
    return;
  }

  const data = await res.json();
  pollDecision(data.taskId);
}

/* ---------------- FEEDBACK ---------------- */

function showFeedbackHint() {
  const el = document.getElementById("feedbackHint");
  el.classList.remove("hidden");

  setTimeout(() => {
    el.classList.add("hidden");
  }, 60000);
}

async function sendFeedback(delta) {
  if (!currentDecisionId) {
    console.warn("No decisionId, feedback ignored");
    return;
  }

  setFeedbackEnabled(false);

  await fetch(`${API}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decisionId: currentDecisionId,
      positionDelta: delta,
    }),
  });

  const msg = document.getElementById("feedbackMessage");
  msg.classList.remove("hidden");

  setTimeout(() => {
    msg.classList.add("hidden");
  }, 3000);

  currentDecisionId = null;

  loadLearningChartForDriver(userSelect.value);
  resetForm();
  checkRetrainStatus();
}

function resetForm() {
  lap.value = "";
  position.value = "";
  tyreLife.value = "";
  lapTime.value = "";

  tyre.value = "SOFT";
  updateTyreColor();

  document.getElementById("tyreFill").style.width = "0%";
  document.getElementById("decisionText").innerText = "Awaiting telemetry…";
  document.getElementById("reasonText").innerText = "";
}
function useGuest() {
  const guestId = "guest-" + crypto.randomUUID();

  const sel = document.getElementById("userSelect");
  const opt = document.createElement("option");

  opt.value = guestId;
  opt.textContent = "Guest session";
  opt.style.color = "#888";

  sel.appendChild(opt);
  sel.value = guestId;

  sessionStorage.setItem("guestUser", guestId);
  resetLearningChart();
}
function resetLearningChart() {
  if (learningChart) {
    learningChart.destroy();
    learningChart = null;
  }
}
window.addEventListener("beforeunload", async () => {
  const guest = sessionStorage.getItem("guestUser");
  if (!guest) return;

  await fetch(`${API}/api/session/end`, {
    method: "POST",
  });

  sessionStorage.removeItem("guestUser");
});
function handleDecision(data) {
  document.getElementById("loader").classList.add("hidden");

  const radio = document.getElementById("decisionText");
  const reasonBox = document.getElementById("reasonText");

  radio.classList.add("static");
  radio.innerText = "📻 RADIO…";

  setTimeout(() => {
    radio.classList.remove("static");
    radio.innerText = data.action === "PIT" ? "BOX BOX" : "STAY OUT";

    const parts = [];
    if (data.reason) parts.push(data.reason);
    if (data.suggestedTyre) parts.push(`Next tyre ${data.suggestedTyre}`);

    reasonBox.innerText = parts.join(" · ");
  }, 700);

  currentDecisionId = data.decisionId;
  showFeedbackHint();
  setFeedbackEnabled(true);
}

async function pollDecision(taskId) {
  const interval = setInterval(async () => {
    const res = await fetch(`${API}/api/decisions/${taskId}`);
    const data = await res.json();

    // SAFETY GUARD
    if (!data || !data.status) {
      return;
    }

    if (data.status === "Queued" || data.status === "Processing") {
      return;
    }

    if (data.status === "Done") {
      clearInterval(interval);
      handleDecision(data);
      currentDecisionId = data.decisionId;
      return;
    }
  }, 500);
}

let learningChart = null;

async function loadLearningChartForDriver(userId) {
  console.log("Learning chart called for:", userId);

  const canvas = document.getElementById("learningChart");
  if (!canvas) {
    console.warn("Canvas not ready yet");
    return;
  }

  const res = await fetch(`${API}/api/learning-stats/${userId}`);
  const data = await res.json();

  if (!data || data.length === 0) {
    if (learningChart) learningChart.destroy();
    return;
  }

  const labels = data.map((d) => d.step);
  const rewards = data.map((d) => d.avgReward);

  const ctx = document.getElementById("learningChart").getContext("2d");

  if (learningChart) {
    learningChart.destroy();
  }

  learningChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Average Reward",
          data: rewards,
          borderWidth: 2,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: "Decisions" },
        },
        y: {
          min: -1,
          max: 1,
          ticks: {
            stepSize: 0.5,
          },
          title: { display: true, text: "Avg Reward" },
        },
      },
    },
  });
}
async function checkRetrainStatus() {
  const res = await fetch(`${API}/api/retrain/status`);
  const data = await res.json();

  const btn = document.getElementById("retrainBtn");
  const info = document.getElementById("retrainInfo");

  if (!btn) return;

  btn.disabled = !data.enabled;

  info.innerText = data.enabled
    ? `Ready (${data.current}/${data.threshold})`
    : `Not enough data (${data.current}/${data.threshold})`;
}
async function triggerRetrain() {
  const btn = document.getElementById("retrainBtn");
  btn.disabled = true;
  btn.innerText = "Retraining...";

  const res = await fetch(`${API}/api/retrain`, {
    method: "POST",
  });

  const data = await res.json();

  alert(
    data.status === "success"
      ? "Agent retrained successfully"
      : "Retraining skipped"
  );

  btn.innerText = "Retrain Agent";
  checkRetrainStatus();
}
