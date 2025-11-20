// Base URL (FastAPI running with uvicorn)
const BASE_URL = "http://127.0.0.1:8000/v1";

// Helper to read the optional paper link from the top input
function getPaperLink() {
  const el = document.getElementById("paperLinkInput");
  return el ? el.value.trim() : "";
}

// ------------- 1. Upload & Index ------------- //

async function handleUpload() {
  const fileInput = document.getElementById("pdfFile");
  const statusEl = document.getElementById("uploadStatus");
  statusEl.textContent = "";

  if (!fileInput.files || fileInput.files.length === 0) {
    statusEl.textContent = "Please choose a PDF file first.";
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  try {
    statusEl.textContent = "Uploading & indexing…";

    const resp = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Upload failed: ${resp.status} – ${err}`);
    }

    const data = await resp.json();
    statusEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    console.error(err);
    statusEl.textContent = String(err);
  }
}

// ------------- 2. Retriever only ------------- //

async function handleRetrieverQuery() {
  const q = document.getElementById("retrieverQuestion").value.trim();
  const topK = parseInt(document.getElementById("retrieverTopK").value, 10) || 6;
  const mode = document.getElementById("retrieverMode").value;
  const out = document.getElementById("retrieverResults");

  out.textContent = "";

  if (!q) {
    out.textContent = "Please type a query.";
    return;
  }

  try {
    out.textContent = "Querying…";

    const resp = await fetch(`${BASE_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: q,
        top_k: topK,
        mode: mode,
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Query failed: ${resp.status} – ${err}`);
    }

    const data = await resp.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    console.error(err);
    out.textContent = String(err);
  }
}

// ------------- 3. LLM-grounded QA ------------- //

async function handleGetAnswer() {
  const question = document.getElementById("qaQuestion").value.trim();
  const topK = parseInt(document.getElementById("qaTopK").value, 10) || 6;
  const mode = document.getElementById("qaMode").value;
  const model = document.getElementById("qaModel").value;

  const ansEl = document.getElementById("qaAnswer");
  const srcEl = document.getElementById("qaSources");

  ansEl.textContent = "";
  srcEl.textContent = "";

  if (!question) {
    ansEl.textContent = "Please type a question.";
    return;
  }

  try {
    ansEl.textContent = "Thinking…";

    const resp = await fetch(`${BASE_URL}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        top_k: topK,
        mode: mode,
        provider: "ollama", // we only use local Ollama
        model: model,       // mistral / llama3 / phi3
      }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Answer failed: ${resp.status} – ${err}`);
    }

    const data = await resp.json();

    // Show answer text
    let answerText = data.answer || "";
    const link = getPaperLink();
    if (link) {
      answerText = `Paper link: ${link}\n\n` + answerText;
    }
    ansEl.textContent = answerText;

    // Show sources
    if (data.used_chunks) {
      srcEl.textContent = JSON.stringify(data.used_chunks, null, 2);
    } else {
      srcEl.textContent = "(no chunks returned)";
    }
  } catch (err) {
    console.error(err);
    ansEl.textContent = String(err);
  }
}

// ------------- 4. Summarize Corpus ------------- //

async function handleSummarize() {
  const maxChunks =
    parseInt(document.getElementById("sumMaxChunks").value, 10) || 12;
  const includeLink = document.getElementById("sumIncludeLink").checked;
  const out = document.getElementById("sumOutput");

  out.textContent = "Summarizing…";

  try {
    const resp = await fetch(`${BASE_URL}/summarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ max_chunks: maxChunks }),
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Summarize failed: ${resp.status} – ${err}`);
    }

    const data = await resp.json();
    let text = data.summary || "";

    const link = getPaperLink();
    if (includeLink && link) {
      text = `Paper link: ${link}\n\n` + text;
    }

    out.textContent = text;
  } catch (err) {
    console.error(err);
    out.textContent = String(err);
  }
}

// ------------- Wire up buttons ------------- //

window.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("btnUpload")
    .addEventListener("click", handleUpload);

  document
    .getElementById("btnRetrieverQuery")
    .addEventListener("click", handleRetrieverQuery);

  document
    .getElementById("btnGetAnswer")
    .addEventListener("click", handleGetAnswer);

  document
    .getElementById("btnSummarize")
    .addEventListener("click", handleSummarize);
});
