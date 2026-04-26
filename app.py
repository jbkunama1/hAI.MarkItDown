from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from markitdown import MarkItDown
import tempfile
import os
import shutil

app = FastAPI(title="MarkItDown WebUI")
md = MarkItDown()

HTML = """
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>MarkItDown WebUI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {
      --bg: #f6f8fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #0f766e;
      --accent-hover: #115e59;
      --border: #d1d5db;
      --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #eef6ff 0%, #f7fafc 45%, #eefaf6 100%);
      color: var(--text);
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .hero {
      margin-bottom: 24px;
      background: var(--card);
      border: 1px solid rgba(15, 118, 110, 0.15);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 24px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 2rem;
    }
    p {
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }
    .grid {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 20px;
    }
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 20px;
    }
    .panel h2 {
      margin-top: 0;
      font-size: 1.15rem;
    }
    input[type=file] {
      display: block;
      width: 100%;
      margin: 14px 0;
      padding: 12px;
      border: 1px dashed var(--border);
      border-radius: 12px;
      background: #f9fafb;
    }
    button {
      background: var(--accent);
      color: #fff;
      border: 0;
      border-radius: 10px;
      padding: 12px 18px;
      cursor: pointer;
      font-weight: 700;
    }
    button:hover { background: var(--accent-hover); }
    .status {
      margin-top: 12px;
      font-size: 14px;
      color: var(--muted);
      min-height: 20px;
    }
    textarea {
      width: 100%;
      min-height: 560px;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      font-family: Consolas, monospace;
      font-size: 14px;
      line-height: 1.5;
      resize: vertical;
      background: #fcfcfd;
    }
    .hint {
      margin-top: 12px;
      font-size: 13px;
      color: var(--muted);
    }
    .badge {
      display: inline-block;
      margin-bottom: 10px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(15, 118, 110, 0.12);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .02em;
    }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      textarea { min-height: 420px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="badge">LAN WebUI • Port 3210</div>
      <h1>MarkItDown WebUI</h1>
      <p>Datei im Browser hochladen und direkt in Markdown umwandeln.</p>
    </div>

    <div class="grid">
      <div class="panel">
        <h2>Upload</h2>
        <form id="uploadForm">
          <input type="file" id="file" name="file" required />
          <button type="submit">Konvertieren</button>
          <div class="status" id="status">Bereit.</div>
        </form>
        <div class="hint">Tipp: Danach kannst du die Ausgabe direkt kopieren oder als Datei speichern.</div>
      </div>

      <div class="panel">
        <h2>Markdown-Ausgabe</h2>
        <textarea id="output" placeholder="Markdown-Ausgabe erscheint hier..."></textarea>
      </div>
    </div>
  </div>

  <script>
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("file");
    const output = document.getElementById("output");
    const status = document.getElementById("status");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!fileInput.files.length) {
        status.textContent = "Bitte eine Datei auswählen.";
        return;
      }

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      status.textContent = "Konvertiere...";
      output.value = "";

      try {
        const res = await fetch("/convert", { method: "POST", body: formData });
        if (!res.ok) {
          const err = await res.text();
          status.textContent = "Fehler bei der Konvertierung.";
          output.value = err;
          return;
        }
        output.value = await res.text();
        status.textContent = "Fertig.";
      } catch (err) {
        status.textContent = "Server nicht erreichbar.";
        output.value = String(err);
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@app.post("/convert", response_class=PlainTextResponse)
async def convert(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        shutil.copyfileobj(file.file, tmp)
        tmp.close()
        result = md.convert(tmp.name)
        return result.text_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
