const BASE_URL = window.location.origin;

document.addEventListener("DOMContentLoaded", () => {
  const carId = localStorage.getItem("selectedCar");
  const carImg = document.getElementById("carImg");

  if (!carImg) return;

  if (!carId) {
    carImg.src = "images/1_after_shape.png";
    return;
  }

  const imgPath = `images/${carId}_after_shape.png`;

  carImg.onerror = () => {
    carImg.src = "images/1_after_shape.png";
  };

  carImg.src = imgPath;

  explainDrag(0, 0);
});

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



async function explainDrag(before, after) {
  try {

    const rawId = localStorage.getItem("selectedCar");

    const modelId = `model_${String(rawId || "1").padStart(2, "0")}`;

    const res = await fetch(`${BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_id: modelId
      })
    });

    const data = await res.json();

    console.log("🧠 AI explain =", data);

    const box = document.getElementById("aiExplanation");
    if (!box) return;

    const explanation =
      data.explanation ||
      data.analysis?.explanation || data.error ||
      "No explanation returned.";

    box.innerText = explanation;
    box.style.whiteSpace = "pre-line";

    if (window.MathJax) {
      MathJax.typesetPromise([box]);
    }

  } catch (err) {
    console.error("❌ explainDrag failed:", err);
  }
}
