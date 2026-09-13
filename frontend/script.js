const BASE_URL = window.location.origin;
let selectedCar = "";
//let cachedPressureData = null;

document.addEventListener("DOMContentLoaded", function () {
  // ======================
  // 🎯 HOTSPOT CLICK
  // ======================
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

// ======================
// 🚗 PRESSURE LOGIC
// ======================
async function selectCar(carId) {
  selectedCar = carId;
  localStorage.setItem("selectedCar", carId);

  const preview = document.getElementById("preview");
  if (preview) {
    preview.src = `images/${carId}_before_shape.png`;
  }
}

function openCarModal(images, title) {
    const modal = document.getElementById("carModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalImages = document.getElementById("modalImages");

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
    modalTitle.innerText = title;

    modalImages.innerHTML = `
      <div class="compare-grid">


        <div class="block">
          <div class="pair-title">Shape</div>
          <div class="pair-row">
            <div class="item">
              <p>Before</p>
              <img src="${images[0]}">
            </div>

            <div class="arrow">→</div>

            <div class="item">
              <p>After</p>
              <img src="${images[1]}">
            </div>
          </div>
        </div>


        <div class="block">
          <div class="pair-title">Pressure</div>
          <div class="pair-row">
            <div class="item">
              <p>Before</p>
              <img src="${images[2]}">
            </div>

            <div class="arrow">→</div>

            <div class="item">
              <p>After</p>
              <img src="${images[3]}">
            </div>
          </div>
        </div>

      </div>
    `;
}

function analyzeSelectedCar() {

  const car = selectedCar || localStorage.getItem("selectedCar");

  if (!car) {
    alert("Please select a car first!");
    return;
  }

  const btn = document.querySelector("button");
  if (btn) {
    btn.innerText = "Analyzing...";
    btn.disabled = true;
  }

  setTimeout(() => {
    window.location.href = "select.html";
  }, 800);
}


// ======================
// 🌐 NAVIGATION
// ======================
function go(page) {

  if (page === "pressure") {
    window.location.href = "pressure.html";
  }

  if (page === "drag") {
    window.location.href = "drag.html";
  }

  if(page === "shape"){
    window.location.href = "shape.html";
  }

  if (page === "model") {
    window.location.href = "model.html";
  }
}

function goBack() {
  window.location.href = "index.html";
}


// ======================
// 🧠 CENTER TEXT (DRAG GAUGE)
// ======================
function centerTextPlugin(value) {
  return {
    id: 'centerText',
    beforeDraw(chart) {

      const { width, height, ctx } = chart;

      ctx.save();

      const fontSize = height / 8;
      ctx.font = `bold ${fontSize}px Arial`;
      ctx.fillStyle = "#9bb3b9";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      ctx.fillText(value + "%", width / 2, height / 2);

      ctx.restore();
    }
  };
}

// model
function openModal(type) {

  const modal = document.getElementById("modal");
  const text = document.getElementById("modalText");

  switch(type) {
    case "drag":
      text.innerHTML = "🚗 Drag: This area influences air resistance.";
      break;

    case "pressure":
      text.innerHTML = "💨 Pressure: AI detects pressure distribution here.";
      break;

    case "efficiency":
      text.innerHTML = "⚡ Efficiency: Optimization improves performance.";
      break;
  }

  modal.style.display = "block";
}

function closeModal() {
  const carModal = document.getElementById("carModal");
  const modal = document.getElementById("modal");

  if (carModal) carModal.style.display = "none";
  if (modal) modal.style.display = "none";

  document.body.style.overflow = "auto";
}

//chatbox
// ======================
// 🤖 AI CHAT FUNCTION
// ======================

function addMessage(text, sender) {

  const box = document.getElementById("chatMessages");

  const msg = document.createElement("div");
  msg.className = sender === "user" ? "msg-user" : "msg-ai";

  msg.innerText = text;

  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
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
