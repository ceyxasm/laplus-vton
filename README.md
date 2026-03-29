# LaPlus VTON - Virtual Try-On Demo

AI-powered virtual try-on for tomorrow's client demo. Take a photo, see yourself wearing any garment.

---

## Quick Start (30 Seconds)

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m app.main

# Terminal 2: Frontend
cd frontend
npm run dev
```

**URLs:**
- Desktop: http://localhost:5173
- Mobile (same WiFi): http://192.168.1.35:5173
- Mobile (ngrok): https://proapostolic-unputatively-neil.ngrok-free.dev

---

## ✅ YOUR TODO (Before Demo Tomorrow)

### High Priority
- [ ] **Test on demo phone** - Full flow with camera
- [ ] **Practice 2-3 times** - Get familiar with flow
- [ ] **Test both cameras** - Front and rear work
- [ ] **Charge demo device** - Don't run out mid-demo
- [ ] **Have backup photos** - Pre-captured images ready
- [ ] **Verify Gemini works** - Or switch to mock mode

### Medium Priority
- [ ] Test network failure scenario
- [ ] Prepare demo talking points
- [ ] Know where to click/what to say
- [ ] Have desktop version ready (backup)

---

## 🔴 KNOWN ISSUES (Might Break During Demo)

### Critical
1. **No job persistence** - Backend restart = all jobs lost
2. **No timeout handling** - Gemini might hang forever
3. **No error fallback** - If API fails, app crashes
4. **Path issues** - Garment images might not load
5. **No rate limiting** - Can spam Gemini API

### Workarounds
- **If Gemini hangs**: Restart backend, try again
- **If images don't load**: Check backend logs, restart
- **If phone won't connect**: Use ngrok URL
- **If everything breaks**: Switch to desktop demo

---

## 📱 Demo Script (2-3 Minutes)

1. **Browse Products** (15 sec)
   - "We have 15 fashion items across 6 categories"
   - Scroll through catalog, show filters

2. **Select Product** (5 sec)
   - Click on a dress or shirt
   - Show product details

3. **Try On** (5 sec)
   - Hit "Try On with Camera"
   - Camera opens instantly

4. **Capture Photo** (10 sec)
   - Show front/rear camera toggle
   - Take clear photo
   - Preview shows immediately

5. **Optional Prompt** (10 sec)
   - "Add custom styling: 'Make it casual'"
   - Show this is configurable

6. **Processing** (15-30 sec)
   - Progress bar fills smoothly
   - "Generating your look..."
   - No blank screens

7. **Reveal Result** (15 sec)
   - AI-generated try-on image
   - "Photorealistic, powered by Gemini"

8. **Regenerate** (optional, 20 sec)
   - Click regenerate
   - "Try: 'Add a jacket'"
   - Show iteration capability

**Total**: ~2-3 minutes

---

## 🛠️ Troubleshooting

### Camera Not Working
- **Cause**: Needs HTTPS or localhost
- **Fix**: Use ngrok URL (has HTTPS) or localhost

### Phone Can't Connect to 192.168.1.35:5173
- **Cause**: Not on same WiFi or AP isolation
- **Fix**: Use ngrok URL instead

### "Blocked host" Error on ngrok
- **Cause**: Vite host checking
- **Fix**: Already added to allowedHosts, restart Vite if needed

### Gemini Taking Forever
- **Cause**: Slow API or large images
- **Fix**: Wait 30s, or restart and try smaller image

### "No such file or directory" Error
- **Cause**: Garment image path wrong
- **Fix**: Restart backend (already fixed in code)

### Backend Crash
- **Cause**: Exception in Gemini service
- **Fix**: Check /tmp/backend_output.log, restart

---

## 🔧 Configuration

### Enable/Disable Features

**Custom Prompts** (edit `frontend/src/pages/TryOn.tsx`):
```typescript
const ENABLE_CUSTOM_PROMPT = true; // Set to false to hide
```

**Gemini API** (edit `backend/.env`):
```env
GEMINI_API_KEY=your_key_here
MOCK_MODE=False  # True = fake results (fast)
MOCK_DELAY=3     # Seconds for mock mode
```

---

## 📋 Backup Plans

### Plan A: Real Gemini (Best)
- Uses Gemini 2.5 Flash Image
- Real AI-generated try-ons
- Takes 10-20 seconds
- **Risk**: Might be slow or fail

### Plan B: Mock Mode (Safe)
- Returns user photo as result
- Takes 3 seconds
- Always works
- **Say**: "This is the flow, real AI is connected"

### Plan C: Desktop Only (Fallback)
- Skip phone, demo on laptop
- Use localhost:5173
- Less impressive but works
- Have this ready

### Plan D: Pre-Generated (Emergency)
- Have 2-3 try-on images ready
- Show them if live demo fails
- "Here's what it generates"

---

## 🚀 Running on Phone

### Option 1: Local Network (Preferred if WiFi works)
1. Both servers running
2. Phone on same WiFi
3. Open: http://192.168.1.35:5173

### Option 2: ngrok (More Reliable)
1. ngrok already running
2. Works from any network
3. Open: https://proapostolic-unputatively-neil.ngrok-free.dev
4. Click "Visit Site" on ngrok warning

---

## 💡 Demo Tips

**Do:**
- Show camera toggle (impressive)
- Mention "mobile-first design"
- Highlight async processing (no frozen screens)
- Show notification when ready
- Demo regenerate feature

**Don't:**
- Rush through - let images load
- Use bad lighting (camera quality matters)
- Forget to charge device
- Assume WiFi will work
- Demo without practicing first

**Talking Points:**
- "AI-powered using Google Gemini"
- "Mobile-optimized for on-the-go shopping"
- "Async processing - no waiting"
- "Custom styling prompts for personalization"
- "Ready to scale with proper deployment"

---

## 📦 What's Built

**Frontend:**
- Product catalog with 15 items
- Category filters
- Product detail pages
- Camera component (front/rear)
- Try-on flow
- Progress tracking
- Notifications
- Regenerate function

**Backend:**
- FastAPI with async processing
- Gemini 2.5 Flash Image integration
- Job polling system
- Image upload/storage
- Product API
- CORS configured

**Deployment:**
- Local dev servers
- ngrok tunnel for mobile
- Ready for Vercel + Railway

---

## 🔗 Important URLs

- **Backend Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Frontend Local**: http://localhost:5173
- **Frontend Network**: http://192.168.1.35:5173
- **Frontend ngrok**: https://proapostolic-unputatively-neil.ngrok-free.dev

---

## 📁 Project Structure

```
V1/
├── backend/          # FastAPI server
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Gemini integration
│   │   └── models/   # Data models
│   ├── uploads/      # User photos & results
│   └── .env          # Config (Gemini key here)
├── frontend/         # React app
│   ├── src/
│   │   ├── pages/    # Catalog, Product, TryOn
│   │   └── components/ # Camera
│   └── public/products/ # 15 product images
├── archive/          # Old documentation
├── README.md         # This file
└── NOTES.md          # Technical notes
```

---

## ❓ Questions?

**Q: Will it work on phone?**
A: Yes, mobile-first design. Use ngrok if local network fails.

**Q: What if Gemini is slow?**
A: Wait up to 30s. Or use mock mode for fast demo.

**Q: What if it breaks during demo?**
A: Have backup photos ready. Switch to desktop. Explain the concept.

**Q: Is this production-ready?**
A: No - it's a POC. Needs database, proper deployment, error handling for production.

**Q: Can I customize it?**
A: Yes, edit .env for config, TryOn.tsx for features.

---

## 🎯 Success Criteria

Demo is successful if you show:
1. ✅ Product browsing works
2. ✅ Camera opens and captures
3. ✅ Processing is smooth (progress bar)
4. ✅ Result displays (real or mock)
5. ✅ Mobile experience is good

**Don't worry about perfection** - it's a POC to show the concept.

---

**Good luck with the demo tomorrow! 🚀**
