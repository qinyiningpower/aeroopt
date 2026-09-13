const BASE_URL = window.location.origin;
let shapeCache = null;
let shapeCarId = null;
let shapeModel = null;

document.addEventListener("DOMContentLoaded", async () => {

  // ======================

  // ======================
  const carId = localStorage.getItem("selectedCar");

  if (carId) {
    await selectCar(carId);
  }

  // ======================

  // ======================
  const carImg = document.getElementById("carImg");

  if (carImg) {
    if (!carId) {
      carImg.src = "images/1_after_shape.png";
    } else {
      const imgPath = `images/${carId}_after_shape.png`;

      carImg.onerror = () => {
        carImg.src = "images/1_after_shape.png";
      };

      carImg.src = imgPath;
    }
  }

  // ======================

  // ======================
  const dots = document.querySelectorAll(".dot");

  dots.forEach(dot => {
    dot.addEventListener("click", () => {

      dots.forEach(d => d.classList.remove("active"));
      dot.classList.add("active");

      const area = dot.getAttribute("data-type");
      showShape(area);
    });
  });

});

async function selectCar(carId) {

  const modelId = `model_${String(carId).padStart(2, "0")}`;

  const res = await fetch(`${BASE_URL}/switch_model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_id: modelId })
  });

  const data = await res.json();

  currentModel = data.current_model || modelId;
}

// ======================
// LOAD API
// ======================
async function loadShapeData() {

  const carId = localStorage.getItem("selectedCar");

  const resModel = await fetch(`${BASE_URL}/models`);
  const modelData = await resModel.json();
  const model = modelData.current_model;

  const res = await fetch(
    `${BASE_URL}/shape_regions?car=${carId}&model=${model}`
  );

  const json = await res.json();

  shapeCache = json.data;
  shapeCarId = carId;
  shapeModel = model;

  return shapeCache;
}
// ======================
// SHOW
// ======================
async function showShape(area) {

  const box = document.getElementById("infoBox");
  box.innerHTML = "⏳ Loading...";

  const carId = localStorage.getItem("selectedCar");

  // ⭐ 1. backend model check
  const resModel = await fetch(`${BASE_URL}/models`);
  const modelData = await resModel.json();
  const backendModel = modelData.current_model;

  if (!shapeCache || shapeCarId !== carId || shapeModel !== backendModel) {
    shapeCache = await loadShapeData();
    shapeModel = backendModel;
  }

  const item = shapeCache.find(d => d.region_id === area);

  if (!item) {
    box.innerHTML = "⚠️ No data for: " + area;
    return;
  }

  const displacement = item.average_displacement;
  const max = item.max_displacement;

  box.innerHTML = `
    <b>Area:</b> ${area}<br>
    <b>Average:</b> ${displacement}<br>
    <b>Max:</b> ${max}<br>
    <hr>
    <b>🧠 AI Insight:</b><br>
    <i>Loading...</i>
  `;

  await explainShape(area, {
    average: displacement,
    max: max
  });
}

// ======================
// AI
// ======================
async function explainShape(area, data) {

  const res = await fetch(`${BASE_URL}/explain_shape`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },

    body: JSON.stringify({
      zone_name: area,
      question: `Explain shape change:
      Average: ${data.average}
      Max: ${data.max}`
    })
  });

  const result = await res.json();

  document.getElementById("infoBox").innerHTML = `
    <b>Area:</b> ${area}<br>
    <b>Average:</b> ${data.average}<br>
    <b>Max:</b> ${data.max}<br>
    <hr>
    <b>🧠 AI Insight:</b><br>
    <div style="white-space: pre-wrap; text-align: left;">
      ${escapeHTML(result.explanation || result.error || "No explanation")}
    </div>
  `;

  if (window.MathJax?.typesetPromise) {
    MathJax.typesetPromise();
  }
}

function addMessage(text, sender) {

  const box = document.getElementById("chatMessages");

  const msg = document.createElement("div");
  msg.className = sender === "user" ? "msg-user" : "msg-ai";

  msg.innerText = text;

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
