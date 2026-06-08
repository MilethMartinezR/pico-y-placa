const fileInput   = document.getElementById("file-input");
const preview     = document.getElementById("preview");
const previewBox  = document.getElementById("preview-container");
const validateBtn = document.getElementById("validate-btn");
const citySelect  = document.getElementById("city");
const resultSec   = document.getElementById("result-section");
const resultCard  = document.getElementById("result-card");
const errorMsg    = document.getElementById("error-msg");

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  previewBox.hidden = false;
  validateBtn.disabled = false;
});

validateBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  validateBtn.disabled = true;
  validateBtn.textContent = "Analizando…";
  resultSec.hidden = true;
  errorMsg.hidden = true;

  const form = new FormData();
  form.append("image", file);
  form.append("city", citySelect.value);

  try {
    const res = await fetch("/validate", { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Error desconocido");
      return;
    }

    showResult(data);
  } catch (err) {
    showError("Error de red. Intenta de nuevo.");
  } finally {
    validateBtn.disabled = false;
    validateBtn.textContent = "Verificar";
  }
});

function showResult(data) {
  resultCard.className = "card " + (data.restricted ? "restricted" : "allowed");

  document.getElementById("plate-text").innerHTML  = `<span>Placa:</span> ${data.plate}`;
  document.getElementById("city-text").innerHTML   = `<span>Ciudad:</span> ${data.city}`;
  document.getElementById("status-text").innerHTML =
    `<span>Estado:</span> ${data.restricted ? "🚫 CON RESTRICCIÓN" : "✅ SIN RESTRICCIÓN"}`;
  document.getElementById("reason-text").innerHTML = `<span>Motivo:</span> ${data.reason}`;
  document.getElementById("time-text").innerHTML   = `<span>Consultado:</span> ${data.checked_at}`;

  resultSec.hidden = false;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.hidden = false;
}
