const form = document.getElementById("qr-form");
const fileInput = document.getElementById("file-input");
const generateBtn = document.getElementById("generate-btn");
const messageEl = document.getElementById("form-message");
const resultEl = document.getElementById("result");
const previewEl = document.getElementById("qr-preview");
const fileLinkEl = document.getElementById("file-link");
const savedNameEl = document.getElementById("saved-name");
const downloadBtn = document.getElementById("download-btn");
const maxUploadSizeBytes = 5 * 1024 * 1024;

let generatedImage = "";
let generatedFilename = "qr-code.png";

function setMessage(text, type = "") {
  messageEl.textContent = text;
  messageEl.className = "form-message";

  if (type) {
    messageEl.classList.add(`is-${type}`);
  }
}

function resetResult() {
  generatedImage = "";
  generatedFilename = "qr-code.png";
  previewEl.removeAttribute("src");
  fileLinkEl.removeAttribute("href");
  fileLinkEl.textContent = "";
  savedNameEl.textContent = "";
  downloadBtn.disabled = false;
  resultEl.hidden = true;
}

async function dataUrlToBlob(dataUrl) {
  const response = await fetch(dataUrl);
  return response.blob();
}

async function readResponsePayload(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return { error: text || "Server xatolik qaytardi." };
}

async function uploadSelectedFile() {
  const selectedFile = fileInput.files?.[0];

  if (!selectedFile) {
    setMessage("Avval fayl tanlang.", "error");
    fileInput.focus();
    return;
  }

  if (selectedFile.size > maxUploadSizeBytes) {
    setMessage("Fayl hajmi 5 MB dan oshmasligi kerak.", "error");
    fileInput.value = "";
    fileInput.focus();
    return;
  }

  generateBtn.disabled = true;
  fileInput.disabled = true;
  generateBtn.textContent = "Yuklanmoqda...";
  setMessage("Fayl saqlanmoqda va QR tayyorlanmoqda...");
  resetResult();

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const payload = await readResponsePayload(response);

    if (!response.ok) {
      throw new Error(payload.error || "QR yasab bo'lmadi.");
    }

    generatedImage = payload.image;
    generatedFilename = payload.qrFilename || "qr-code.png";
    previewEl.src = generatedImage;
    fileLinkEl.href = payload.fileUrl;
    fileLinkEl.textContent = payload.fileUrl;
    savedNameEl.textContent = `Saqlangan nom: ${payload.storedFilename}`;
    downloadBtn.disabled = false;
    resultEl.hidden = false;
    setMessage("Fayl saqlandi. Link va QR tayyor.", "success");
  } catch (error) {
    setMessage(error.message || "Xatolik yuz berdi.", "error");
  } finally {
    generateBtn.disabled = false;
    fileInput.disabled = false;
    generateBtn.textContent = "Yuklash";
  }
}

fileInput.addEventListener("change", () => {
  resetResult();
  setMessage("");

  if (fileInput.files?.length) {
    uploadSelectedFile();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  uploadSelectedFile();
});

downloadBtn.addEventListener("click", async () => {
  if (!generatedImage) {
    setMessage("Avval fayl yuklang.", "error");
    return;
  }

  downloadBtn.disabled = true;
  setMessage("QR fayl yuklanmoqda...", "success");

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
      downloadBtn.disabled = false;
    }, 500);
  } catch {
    downloadBtn.disabled = false;
    setMessage("Download ishlamadi. Qaytadan urinib ko'ring.", "error");
  }
});
