const BASE_URL = window.location.origin;
let clickMap = null;
let currentModel = null;

const analyzeBtn = document.getElementById("analyzeBtn");

if (analyzeBtn) {
  analyzeBtn.addEventListener("click", () => {
    window.location.href = "drag.html";
  });
}

document.addEventListener("DOMContentLoaded", () => {

  const carId = localStorage.getItem("selectedCar");

  if (carId) {
    selectCar(carId);
  }

  const dots = document.querySelectorAll(".dot");

  dots.forEach(el => {
    el.addEventListener("click", () => {

      const region = el.getAttribute("data-type");

      console.log("🔥 CLICK:", region);

      if (!region) return;

      // ✅ REMOVE old active
      dots.forEach(d => d.classList.remove("active"));

      // ✅ ADD new active
      el.classList.add("active");

      explainZone(region);
    });
  });

  const carImg = document.getElementById("carImg");

  if (carImg && carId) {
    const imgPath = `images/${carId}_after_pressure.png`;

    carImg.onerror = () => {
      carImg.src = "images/1_after_pressure.png";
    };

    carImg.src = imgPath;
  }

});

async function selectCar(carId) {

  localStorage.setItem("selectedCar", carId);

  const res = await fetch(`${BASE_URL}/switch_model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model_id: `model_${String(carId).padStart(2, "0")}`
    })
  });

  const data = await res.json();

  currentModel = data.current_model;

  // ✅ ADD THIS
  clickMap = await loadClickMap();

  loadDragData();
}

async function loadClickMap() {
  const res = await fetch(`${BASE_URL}/click_map`);
  const json = await res.json();
  return json.data;
}


async function loadDragData() {

  const carId = localStorage.getItem("selectedCar");

  if (!carId) {
    console.warn("No car selected");
    return;
  }



  const res = await fetch(`${BASE_URL}/case_info`);
  const data = await res.json();

  console.log("🔥 DRAG RAW =", data);

  const before = data.drag_before;
  const after = data.drag_after;

  document.getElementById("beforeDrag").innerText = before;
  document.getElementById("afterDrag").innerText = after;

  const reduction = (((before - after) / before) * 100).toFixed(2);
  document.getElementById("reduction").innerText = reduction + "%";

  renderChart(before, after);
  explainDrag(before, after);
}

function renderChart(before, after) {

  const ctx1 = document.getElementById("originalGauge");
  const ctx2 = document.getElementById("optimizedGauge");

  if (!ctx1 || !ctx2) {
    console.log("⚠️ canvas not ready");
    return;
  }

  new Chart(ctx1, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [before * 100, 100 - before * 100],
        backgroundColor: ["#e74c3c", "#eee"]
      }]
    },
    options: { cutout: "70%" }
  });

  new Chart(ctx2, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [after * 100, 100 - after * 100],
        backgroundColor: ["#2ecc71", "#eee"]
      }]
    },
    options: { cutout: "70%" }
  });
}

// ======================
// AI
// ======================
async function explainZone(regionId) {

  const res = await fetch(`${BASE_URL}/explain_drag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      zone_name: regionId.toLowerCase(),// IMPORTANT
    })
  });

  const data = await res.json();

  document.getElementById("infoBox").innerHTML = `
    <b>Region:</b> ${regionId}<br>
    <hr>
    <b>🧠 AI Drag Insight:</b><br>
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


async function explainDrag(before, after) {
  try {
    const res = await fetch(`${BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        drag_before: before,
        drag_after: after
      })
    });

    const data = await res.json();
    console.log("🧠 AI explain =", data);

    const box = document.getElementById("aiExplanation");

    if (!box) return;

    const explanation =
      data.explanation ||
      data.analysis?.explanation ||
      data.analysis?.result ||
      data.analysis?.message ||
      data.analysis?.error ||   // 👈 THIS is your current case
      "No explanation returned.";

    box.innerText = explanation;

    if (window.MathJax) {
      MathJax.typesetPromise([box]);
    }

  } catch (err) {
    console.error("❌ explainDrag failed:", err);
  }
}
