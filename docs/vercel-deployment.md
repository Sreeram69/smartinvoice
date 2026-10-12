# Vercel Deployment & Remote Access Guide

Deploy your **SmartInvoice AI** frontend to **Vercel** for a free, public HTTPS website (`https://your-smartinvoice.vercel.app`) that you can open from anywhere in the world on your Android phone, while keeping all OCR, PDF generation, and SQLite database storage on your local Windows PC.

---

## 1. Why This Architecture?

| Layer | Runs On | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **Vercel** (Global Edge CDN) | Fast, public HTTPS address accessible from anywhere (even mobile data / 4G / 5G) |
| **Backend Engine** | **Your Windows PC** | Tesseract OCR, ReportLab PDF/DOCX generation, Local SQLite database |
| **Connection** | **Secure HTTPS Tunnel** | Allows Vercel's HTTPS frontend to reach your PC without port forwarding or mixed-content blocks |

---

## 2. Deploy Frontend to Vercel (2 Minutes)

### Option A: Via GitHub (Recommended)
1. Push your repository to your GitHub account:
   ```bash
   git add .
   git commit -m "deploy: vercel frontend"
   git push origin main
   ```
2. Log in to [vercel.com](https://vercel.com).
3. Click **Add New...** $\to$ **Project**.
4. Select your **SmartInvoice** repository.
5. In the configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Select `frontend` (or leave as root if deploying just the frontend folder).
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. (Optional) Under **Environment Variables**, add:
   - Name: `VITE_API_BASE_URL`
   - Value: Your tunnel URL (or you can set it directly inside the app).
7. Click **Deploy**!

---

## 3. How to Connect from Your Android Phone from Anywhere

Because Vercel is hosted on HTTPS, your phone cannot reach `http://localhost:8000` on your PC when you are outside your house.

### Step 1: Start Your PC Backend with Tunnel
On your Windows laptop, run:
```powershell
.\scripts\start-tunnel.ps1
```
This automatically starts your FastAPI backend and prints a secure public HTTPS URL, for example:
```text
your url is: https://smart-invoice-pc.loca.lt
```

*(Alternatively, you can use Cloudflare Tunnel `cloudflared tunnel --url http://localhost:8000` or `ngrok http 8000`).*

### Step 2: Open the Vercel App on Your Phone
1. On your phone (on mobile data or any Wi-Fi), open your Vercel link: `https://your-smartinvoice.vercel.app`.
2. Tap the **BACKEND READY / STANDBY** pill in the top header.
3. Paste your tunnel URL: `https://smart-invoice-pc.loca.lt`.
4. Tap **TEST CONNECTION** $\to$ **SAVE & APPLY**.
5. Done! The indicator turns green (**BACKEND READY**).

You can now:
- Snap address photos with your phone camera $\to$ OCR runs on your PC.
- Dictate item names, counts, and prices by voice $\to$ table populates.
- Download professional Invoices, Delivery Challans, and Address Labels directly on your phone!
