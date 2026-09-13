
const BASE_URL = window.location.origin;
let selectedCar = localStorage.getItem("selectedCar");
let clickMap = null;
let pressureCache = null;
let currentModel = null;
let isLoadingData = false;

document.addEventListener("DOMContentLoaded", function () {

  const savedCar = localStorage.getItem("selectedCar");

  if (savedCar) {
    selectCar(savedCar);
  }

  const dots = document.querySelectorAll(".dot");

  dots.forEach(dot => {
    dot.addEventListener("click", function () {

      dots.forEach(d => d.classList.remove("active"));
      this.classList.add("active");

      const type = this.getAttribute("data-type");
      showPressure(type);
    });
  });

});

async function selectCar(carId) {

  selectedCar = carId;
  localStorage.setItem("selectedCar", carId);

  const modelId = `model_${String(carId).padStart(2, "0")}`;

  const res = await fetch(`${BASE_URL}/switch_model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_id: modelId })
  });

  const data = await res.json();
  console.log("switch_model:", data);

  currentModel = modelId;

  clickMap = await loadClickMap();
  pressureCache = await loadPressure();

  console.log("INIT clickMap:", clickMap);
  console.log("INIT pressureCache:", pressureCache);
}
// ======================
// LOAD CLICK MAP
// ======================
async function loadClickMap() {
  const res = await fetch(`${BASE_URL}/click_map`);
  const json = await res.json();

  console.log("🔥 CLICK MAP RAW =", json);

  return json.data;
}

// ======================
// LOAD PRESSURE
// ======================
async function loadPressure() {

  const res = await fetch(`${BASE_URL}/pressure_regions`);
  const json = await res.json();

  return json.data;
}

// ======================
// MAIN CLICK
// ======================
async function showPressure(area) {

  const box = document.getElementById("infoBox");
  box.innerHTML = "⏳ Loading...";


  const resModel = await fetch(`${BASE_URL}/models`);
  const modelData = await resModel.json();

  const backendModel = modelData.current_model;

  console.log("MODEL (backend):", backendModel);
  console.log("MODEL (frontend currentModel):", currentModel);


  if (!clickMap || !pressureCache || currentModel !== backendModel) {
    clickMap = await loadClickMap();
    pressureCache = await loadPressure();
    currentModel = backendModel;

    console.log("🔄 data refreshed for model:", backendModel);
  }

  const mapItem = clickMap.find(d => d.region_id === area);

  if (!mapItem) {
    box.innerHTML = "⚠️ No region mapping: " + area;
    return;
  }

  const regionId = mapItem.region_id;

  const pressureItem = pressureCache.find(
    d => d.region_id === regionId
  );

  const before = pressureItem?.pressure_before_mean;
  const after = pressureItem?.pressure_after_mean;
  const change = pressureItem?.pressure_change;

  if (before === undefined || after === undefined || change === undefined) {
    box.innerHTML = "⚠️ Incomplete pressure data: " + regionId;
    return;
  }

  box.innerHTML = `
  <b>Region:</b> ${regionId}<br>
  <b>Before:</b> ${before}<br>
  <b>After:</b> ${after}<br>
  <b>Change (Δ):</b> ${change}<br>
  <hr>
  <b>🧠 AI Insight:</b><br>
  <i>Loading...</i>
`;

  await explainZone(regionId, {
    before,
    after,
    change
  });
}

// ======================
// AI
// ======================
async function explainZone(regionId, pressure) {

  const res = await fetch(`${BASE_URL}/explain_pressure`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },

    body: JSON.stringify({
      zone_name: regionId,
      question: `Explain pressure change in this region.
      Before: ${pressure.before}
      After: ${pressure.after}
      Change: ${pressure.change}`
    })
  });

  const data = await res.json();

  document.getElementById("infoBox").innerHTML = `
  <b>Region:</b> ${regionId}<br>
  <b>Before:</b> ${pressure.before}<br>
  <b>After:</b> ${pressure.after}<br>
  <b>Change (Δ):</b> ${pressure.change}<br>
  <hr>
  <b>🧠 AI Insight:</b><br>
  <div style="white-space: pre-wrap; text-align: left;">
    ${escapeHTML(data.explanation || data.error || "No explanation")}
  </div>
`;

  if (window.MathJax) {
    MathJax.typeset();
  }
}

function addMessage(text, sender) {

  const box = document.getElementById("chatMessages");

  const msg = document.createElement("div");
  msg.className = sender === "user" ? "msg-user" : "msg-ai";

  msg.textContent = text;

  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;

  if (window.MathJax) {
    MathJax.typeset();
  }
}

function sendMessage() {

  const input = document.getElementById("userInput");
  const message = input.value.trim();

  if (!message) return;


  addMessage(message, "user");
  input.value = "";


  addMessage("Thinking...", "ai");

  fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question: message
    })
  })
  .then(res => res.json())
  .then(data => {


    const msgs = document.querySelectorAll(".msg-ai");
    msgs[msgs.length - 1].remove();


    addMessage(data.answer || JSON.stringify(data), "ai");
  })
  .catch(err => {

    addMessage("❌ Error connecting to AI server", "ai");
    console.error(err);
  });
}
