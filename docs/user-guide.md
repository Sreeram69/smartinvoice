# SmartInvoice AI — User Guide & Operations Manual

SmartInvoice AI is a lightweight, high-precision business automation application engineered with an **Industrial Neo-Minimalist aesthetic inspired by Nothing OS and Teenage Engineering**.

It runs 100% locally on your **Windows PC** and is instantly accessible on your **Android phone** over local Wi-Fi.

---

## 1. Quick Launch

### 1-Click Startup (PowerShell)
Double-click or run from PowerShell:
```powershell
.\scripts\start-dev.ps1
```

This launches two windows:
- **FastAPI Backend**: `http://localhost:8000`
- **Vite Frontend**: `http://localhost:5173` (also displays your phone's Wi-Fi access URL, e.g. `http://10.247.51.19:5173`).

---

## 2. Using SmartInvoice AI on Mobile Phone

1. Make sure your Android phone and Windows laptop are connected to the same Wi-Fi router.
2. Open Chrome or any browser on your phone.
3. Type the Wi-Fi URL displayed in `start-dev.ps1` (e.g. `http://10.247.51.19:5173`).
4. You can use your phone's camera directly to take photos of address labels!

---

## 3. Core Features & Operations

### A. Single-Photograph Address OCR
1. Under **INVOICE**, **CHALLAN**, or **ADDRESS**, scroll to the **SINGLE-PHOTO ADDRESS OCR** card.
2. Click **TAKE PHOTO (CAMERA)** on phone, or **UPLOAD IMAGE FILE** on laptop.
3. The image is processed through Pillow contrast enhancement and OCR.
4. An interactive **CONFIRM OCR EXTRACTED ADDRESSES** card appears:
   - Review the detected Sender (FROM) and Customer (TO).
   - If the roles were inverted in the photo, click **SWAP ROLES**.
   - Edit any name, line, or phone number directly.
   - Click **CONFIRM & APPLY TO DOCUMENT**.

---

### B. Dual Item Entry (Voice & Manual Typing)
You have complete control over item names, counts, and prices:
- **Voice Input**:
  - Click the large circular microphone button.
  - Speak naturally, e.g.:
    - *"Boxes count 10 price 2500"*
    - *"5 chairs price 1200"*
    - *"Laptop 45000"*
  - The item automatically populates in the item table.
- **Manual Input**:
  - Click **ADD ROW** to insert items manually.
  - Edit **Item Name**, **Count / Qty**, and **Price / Amount (₹)** in the table.
- **User-Defined Pricing**:
  - Totals are never locked against your will.
  - The **DOCUMENT TOTAL** field at the bottom allows you to enter any exact final amount.
  - If you want to reset to the exact sum of items, click **RESET AUTO-SUM**.

---

### C. Multi-Format Document Generation
Under **DOCUMENT SETTINGS & DOWNLOAD**:
- **Invoice Number & Date**: Edit or use automatic numbering.
- **Required**: `[✓] Tax Invoice PDF` (or Delivery Challan PDF).
- **Optional Address Label**:
  - Check `[✓] Download Address Label`.
  - Select format: `(•) PDF` or `( ) Word Document (.docx)`.
- Click **GENERATE & DOWNLOAD**:
  - **Unchecked**: Downloads single PDF (`Invoice_INV-XXXX.pdf`).
  - **Checked**: Downloads a single combined **`.ZIP` archive** (`SmartInvoice_INV-XXXX.zip`) containing both documents.

---

### D. Supabase Cloud Archive & History
- Every downloaded invoice or delivery challan is **automatically synced to your Supabase Cloud database**.
- Click the **HISTORY** tab to view all past documents.
- Features:
  - Search by document number or customer name.
  - Filter by `ALL`, `INVOICES`, `CHALLANS`.
  - **OPEN**: Loads that past document into the editor.
  - **PDF**: Re-downloads the PDF directly from the archive.

---

### E. Local n8n Automation
- Whenever a document is generated, SmartInvoice AI sends an asynchronous webhook event to:
  ```text
  http://localhost:5678/webhook/smartinvoice
  ```
- Import the ready-to-use workflows from [`n8n/workflows/`](file:///c:/Users/cheek/OneDrive/Desktop/SmartInvoice/n8n/workflows/):
  - `invoice-created.json`
  - `challan-created.json`
- If local n8n is closed, the app continues to generate and download documents without any delay or error.
