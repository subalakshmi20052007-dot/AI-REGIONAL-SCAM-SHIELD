// --- Voice recording via the browser's built-in Web Speech API ---
// No cloud API key needed. Works in Chrome / Edge. Falls back to
// typing if the browser doesn't support it (e.g. Firefox, Safari).

const transcriptEl = document.getElementById("transcript");
const recordBtn = document.getElementById("recordBtn");
const recStatus = document.getElementById("recStatus");
const scanBtn = document.getElementById("scanBtn");
const resultEl = document.getElementById("result");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let recording = false;

if (!SpeechRecognition) {
  recordBtn.disabled = true;
  recStatus.textContent = "Voice recording isn't supported in this browser — try Chrome, or just type the transcript.";
} else {
  recognizer = new SpeechRecognition();
  recognizer.continuous = true;
  recognizer.interimResults = true;
  // English is the default; swap to 'ta-IN' or 'hi-IN' to record in
  // Tamil or Hindi directly (only one language per session).
  recognizer.lang = "en-IN";

  recognizer.onresult = (event) => {
    let finalText = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalText += event.results[i][0].transcript + " ";
      }
    }
    if (finalText) {
      transcriptEl.value = (transcriptEl.value + " " + finalText).trim();
    }
  };

  recognizer.onerror = (e) => {
    recStatus.textContent = "Mic error: " + e.error;
    stopRecording();
  };

  recognizer.onend = () => {
    if (recording) recognizer.start(); // keep listening until user stops
  };
}

function startRecording() {
  recording = true;
  recognizer.start();
  recordBtn.textContent = "⏹ Stop";
  recordBtn.classList.add("recording");
  recStatus.textContent = "Listening…";
}

function stopRecording() {
  recording = false;
  if (recognizer) recognizer.stop();
  recordBtn.textContent = "🎙 Record";
  recordBtn.classList.remove("recording");
  recStatus.textContent = "";
}

recordBtn?.addEventListener("click", () => {
  if (!recording) startRecording();
  else stopRecording();
});

// --- Scan request ---
scanBtn.addEventListener("click", async () => {
  const transcript = transcriptEl.value.trim();
  if (!transcript) return;

  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning…";

  try {
    const res = await fetch("/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript }),
    });
    const data = await res.json();
    renderResult(data);
  } catch (err) {
    resultEl.innerHTML = `<div class="risk-card">Error reaching the server: ${err}</div>`;
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = "Scan transcript";
  }
});

function renderResult(data) {
  const msgsByLabel = {
    "No risk detected": ["No scam-pattern signals found in this transcript."],
    "Low risk": ["One scam-pattern signal detected.", "Stay alert if the caller pushes further."],
    "Medium risk": ["Multiple scam-pattern signals detected.", "Do not share OTP, KYC, or personal information yet.", "Verify the caller through an official number."],
    "High risk": ["Do not transfer money, share OTP, KYC, or personal information.", "Verify the caller using another trusted method.", "Hang up and report the number if unsure."],
  };
  const msgs = msgsByLabel[data.risk_label] || [];

  resultEl.innerHTML = `
    <div class="risk-card">
      <div class="risk-title">${data.risk_label} — ${data.risk_pct}%</div>
      <div class="risk-sub">${data.matched.length} signal categor${data.matched.length === 1 ? "y" : "ies"} matched</div>
      <div class="risk-msgs">${msgs.map(m => `<div>— ${m}</div>`).join("")}</div>
      <div class="tags">${data.matched.map(m => `<span>${m.category} ("${m.phrase}")</span>`).join("")}</div>
    </div>
  `;
}
