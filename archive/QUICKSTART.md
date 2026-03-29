# Quick Start Guide

Get the LaPlus VTON demo running in 5 minutes.

## Prerequisites Check

```bash
# Check Node.js (need 18+)
node --version

# Check Python (need 3.9+)
python3 --version

# Check npm
npm --version
```

## Step 1: Backend (Terminal 1)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server (will run in mock mode by default)
python -m app.main
```

✅ You should see: "Application startup complete" at http://localhost:8000

## Step 2: Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ You should see: "Local: http://localhost:5173"

## Step 3: Test

**On Desktop:**
- Open http://localhost:5173
- Browse products
- Click "Try On with Camera"

**On Mobile (same network):**
- Find your computer's IP: `ipconfig` or `ifconfig`
- On phone: http://YOUR_IP:5173
- Allow camera permissions

## Step 4: Add Gemini API Key (Optional)

If you want real AI try-on (not mock):

1. Get API key from https://ai.google.dev/
2. Edit `backend/.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   MOCK_MODE=False
   ```
3. Restart backend server

## Troubleshooting

**"Module not found" errors:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

**Camera not working:**
- Use HTTPS or localhost only
- Check browser permissions
- Try Chrome or Safari

**Can't access from phone:**
- Check firewall settings
- Ensure same WiFi network
- Try: http://localhost:5173 on desktop first

**API errors:**
- Keep MOCK_MODE=True for testing
- Check Gemini API key is valid
- Verify both servers are running

## Demo Flow

1. Browse catalog
2. Select product (e.g., "Classic White Shirt")
3. Click "Try On with Camera"
4. Take photo (front camera recommended)
5. (Optional) Add prompt: "Make it casual"
6. Wait 3-5 seconds (mock mode) or 5-10 seconds (real AI)
7. View result!

## Quick Commands

```bash
# Stop servers: Ctrl+C in each terminal

# Restart backend:
cd backend && python -m app.main

# Restart frontend:
cd frontend && npm run dev

# Check backend health:
curl http://localhost:8000/health
```

## For Tomorrow's Demo

**Before Demo:**
- [ ] Both servers running
- [ ] Test on demo phone
- [ ] Camera works
- [ ] 2-3 test runs completed
- [ ] Decide: mock mode or real AI?

**During Demo:**
- Show catalog browsing
- Pick a product
- Show camera (front/rear toggle)
- Take clear photo
- Show optional prompt
- Display processing animation
- Reveal result
- (Optional) Show regenerate

**Backup Plan:**
- Pre-captured photos ready
- Keep MOCK_MODE=True if network issues
- Have desktop version ready if phone fails

Good luck! 🚀
