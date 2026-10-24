const form = document.getElementById("predictionForm");
const resultSection = document.getElementById("resultSection");
const errorBox = document.getElementById("errorBox");
const predictBtn = document.getElementById("predictBtn");
const resetBtn = document.getElementById("resetBtn");
let probabilityChart = null;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");
  predictBtn.disabled = true;
  predictBtn.querySelector("span:first-child").textContent = "Analyzing...";

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prediction request failed.");

    document.getElementById("predictionText").textContent = data.prediction;
    document.getElementById("resultDescription").textContent =
      "The model has completed its estimate using the accident details provided.";
    resultSection.classList.remove("hidden");

    const probabilities = data.probabilities || [];
    const labels = probabilities.map(item => item.label);
    const values = probabilities.map(item => Number(item.percentage));
    const list = document.getElementById("probabilityList");
    list.innerHTML = "";
    probabilities.forEach(item => {
      const card = document.createElement("div");
      card.className = "probability-item";
      const label = document.createElement("span");
      label.textContent = item.label;
      const value = document.createElement("strong");
      value.textContent = `${Number(item.percentage).toFixed(2)}%`;
      card.append(label, value);
      list.appendChild(card);
    });

    const ctx = document.getElementById("probabilityChart");
    if (probabilityChart) probabilityChart.destroy();
    probabilityChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Probability (%)",
          data: values,
          backgroundColor: ["#2879a9", "#4b9bc2", "#91c4dc"],
          borderRadius: 7,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, max: 100, ticks: { callback: value => value + "%" }, grid: { color: "#edf1f5" } },
          y: { grid: { display: false } }
        }
      }
    });
    resultSection.scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.classList.remove("hidden");
    errorBox.scrollIntoView({behavior: "smooth", block: "center"});
  } finally {
    predictBtn.disabled = false;
    predictBtn.querySelector("span:first-child").textContent = "Predict severity";
  }
});

resetBtn.addEventListener("click", () => {
  resultSection.classList.add("hidden");
  errorBox.classList.add("hidden");
  form.reset();
  window.scrollTo({top: 0, behavior: "smooth"});
});
