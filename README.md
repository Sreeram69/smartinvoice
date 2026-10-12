# SmartInvoice AI

A lightweight, high-precision business automation web application running 100% locally on your **Windows PC** (and mobile devices over Wi-Fi), engineered with an **Industrial Neo-Minimalist aesthetic inspired by Nothing OS and Teenage Engineering**.

---

## Key Features

- **Industrial Neo-Minimalist UI**: Pure black surfaces (`#0A0A0A`, `#141414`), subtle hardware dot-matrix DNA (`:::`), and surgical **Nothing Red** (`#EB0029`) accents.
- **Dual Voice & Manual Item Entry**: Add items by speaking (Web Speech API) or typing; direct user control over **Item Name**, **Count / Qty**, and **Price / Amount** (no forced auto-calculations).
- **Single-Photograph Address OCR**: Extract sender and customer addresses from a single photo with an interactive confirmation card and role-swap capability.
- **Professional Multi-Format Documents**: Tax Invoice (PDF), Delivery Challan (PDF), and Address Labels (PDF / Word DOCX).
- **Consolidated ZIP Downloads**: Check the address label box to download both documents in a single `.zip` file for phone and laptop compatibility.
- **Supabase Cloud Persistence**: Automatic background cloud syncing for documents and customer profiles with a searchable History Archive.
- **Local n8n Webhook Integration**: Non-blocking asynchronous event dispatches (`http://localhost:5678`) with zero interruption if n8n is offline.

---

## Quick Start (Local Windows)

### 1-Click Launch (PowerShell)
```powershell
.\scripts\start-dev.ps1
```
This automatically launches:
- **FastAPI Backend**: `http://localhost:8000/docs`
- **Vite Frontend**: `http://localhost:5173`
- **Phone on Wi-Fi**: Displays your local Wi-Fi URL (e.g. `http://10.247.51.19:5173`) to open on your Android phone!

---

## Testing & Quality Assurance

### Run Backend Automated Tests (17 tests)
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

### Build Frontend for Production
```powershell
cd frontend
npm.cmd run build
```

---

## Project Structure

```text
SmartInvoice/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # Health, items, documents, customers, ocr, automation
│   │   ├── core/            # App configuration (.env)
│   │   ├── schemas/         # Pydantic validation models
│   │   ├── services/        # OCR, document generation, Supabase, n8n automation
│   │   └── templates/       # ReportLab PDF & python-docx templates
│   └── tests/               # 17 pytest automated tests
├── frontend/
│   ├── src/
│   │   ├── components/      # Address OCR, Voice/Manual Items, Download Options, History
│   │   ├── hooks/           # Web Speech API recognition hook
│   │   └── index.css        # Nothing OS & Teenage Engineering design system
├── n8n/
│   └── workflows/           # Ready-to-import n8n automation workflows
├── docs/
│   └── user-guide.md        # Comprehensive operations guide
└── scripts/
    └── start-dev.ps1        # 1-click launch script
```
