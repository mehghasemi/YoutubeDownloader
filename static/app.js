const form = document.querySelector("#download-form");
const urlInput = document.querySelector("#url");
const pasteButton = document.querySelector("#paste");
const downloadButton = document.querySelector("#download");
const panel = document.querySelector("#progress-panel");
const statusText = document.querySelector("#status");
const percentText = document.querySelector("#percent");
const progressBar = document.querySelector("#progress");
const speedText = document.querySelector("#speed");
const errorText = document.querySelector("#error");
const fileLink = document.querySelector("#file-link");
let pollTimer = null;

pasteButton.addEventListener("click", async () => {
  try {
    urlInput.value = await navigator.clipboard.readText();
    urlInput.focus();
  } catch {
    urlInput.focus();
    alert("دسترسی به clipboard توسط مرورگر اجازه داده نشد؛ از Ctrl+V استفاده کنید.");
  }
});

function showJob(job) {
  panel.classList.remove("hidden");
  const percent = Math.max(0, Math.min(100, Number(job.percent || 0)));
  statusText.textContent = job.message || "در حال انجام...";
  percentText.textContent = `${Math.round(percent)}٪`;
  progressBar.style.width = `${percent}%`;
  speedText.textContent = job.speed || "";
  errorText.textContent = job.error || "";
  if (job.status === "completed" && job.filename) {
    fileLink.href = `/api/files/${encodeURIComponent(job.filename)}`;
    fileLink.classList.remove("hidden");
  } else {
    fileLink.classList.add("hidden");
  }
}

async function poll(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  const job = await response.json();
  showJob(job);
  if (job.status === "completed" || job.status === "error") {
    downloadButton.disabled = false;
    downloadButton.textContent = "شروع دانلود";
    pollTimer = null;
    return;
  }
  pollTimer = setTimeout(() => poll(jobId), 700);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pollTimer) clearTimeout(pollTimer);
  downloadButton.disabled = true;
  downloadButton.textContent = "در حال دانلود...";
  errorText.textContent = "";
  fileLink.classList.add("hidden");
  panel.classList.remove("hidden");
  statusText.textContent = "در حال ارسال درخواست...";
  try {
    const data = Object.fromEntries(new FormData(form).entries());
    const response = await fetch("/api/download", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "درخواست ناموفق بود.");
    poll(result.job_id);
  } catch (error) {
    showJob({status: "error", message: "خطا", error: error.message});
    downloadButton.disabled = false;
    downloadButton.textContent = "شروع دانلود";
  }
});
