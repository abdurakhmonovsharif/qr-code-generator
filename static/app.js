const form = document.getElementById("qr-form");
const urlInput = document.getElementById("url-input");
const generateBtn = document.getElementById("generate-btn");
const messageEl = document.getElementById("form-message");
const resultEl = document.getElementById("result");
const previewEl = document.getElementById("qr-preview");
const downloadBtn = document.getElementById("download-btn");

let generatedImage = "";
let generatedFilename = "qr-code.png";

function setMessage(text, type = "") {
  messageEl.textContent = text;
  messageEl.className = "form-message";

  if (type) {
    messageEl.classList.add(`is-${type}`);
  }
}

function isValidUrl(value) {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

function resetResult() {
  generatedImage = "";
  generatedFilename = "qr-code.png";
  previewEl.removeAttribute("src");
  downloadBtn.disabled = false;
  resultEl.hidden = true;
}

async function dataUrlToBlob(dataUrl) {
  const response = await fetch(dataUrl);
  return response.blob();
}

urlInput.addEventListener("input", () => {
  if (!resultEl.hidden) {
    resetResult();
  }

  setMessage("");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const rawUrl = urlInput.value.trim();

  if (!isValidUrl(rawUrl)) {
    setMessage("To'g'ri URL kiriting. Masalan: https://example.com", "error");
    urlInput.focus();
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Yasalmoqda...";
  setMessage("QR tayyorlanmoqda...");
  resetResult();

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: rawUrl }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "QR yasab bo'lmadi.");
    }

    generatedImage = payload.image;
    generatedFilename = payload.filename || "qr-code.png";
    previewEl.src = generatedImage;
    downloadBtn.disabled = false;
    resultEl.hidden = false;
    setMessage("QR tayyor. Endi download qilishingiz mumkin.", "success");
  } catch (error) {
    setMessage(error.message || "Xatolik yuz berdi.", "error");
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "QR yasash";
  }
});

downloadBtn.addEventListener("click", async () => {
  if (!generatedImage) {
    setMessage("Avval QR yarating.", "error");
    return;
  }

  downloadBtn.disabled = true;
  setMessage("Download boshlandi. Sahifa yangilanmoqda...", "success");

  try {
    const blob = await dataUrlToBlob(generatedImage);
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = generatedFilename;
    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => {
      URL.revokeObjectURL(objectUrl);
      window.location.reload();
    }, 900);
  } catch {
    downloadBtn.disabled = false;
    setMessage("Download ishlamadi. Qaytadan urinib ko'ring.", "error");
  }
});
