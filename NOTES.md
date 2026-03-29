# Technical Notes & Context

Internal documentation for AI/developer reference. Not for end users.

---

## Implementation Status

### ✅ Completed (Core Features)

**Backend:**
- FastAPI + Python + Pydantic
- Product API (JSON-based, 15 products)
- Image upload endpoint
- Gemini 2.5 Flash Image integration
- Job polling system (in-memory)
- Async processing with asyncio
- CORS configured for mobile
- Error handling (basic)

**Frontend:**
- React 18 + TypeScript + Vite
- Tailwind CSS for styling
- Product catalog with category filters
- Product detail pages
- Camera component (MediaDevices API)
  - Front/rear camera toggle
  - Photo capture and preview
- Try-on flow (4 steps: camera, prompt, processing, result)
- Custom prompt input (config-toggleable)
- Progress bar (0-100%)
- Toast notifications (react-hot-toast)
- Regenerate functionality
- Mobile-responsive design
- Loading states throughout

**Deployment:**
- Local development servers working
- ngrok tunnel configured
- Vite allowedHosts set up for ngrok

**Data:**
- 15 product images downloaded from Unsplash
- Product catalog JSON with descriptions
- Categories: shirts, dresses, jackets, pants, sarees, kurtas

---

### ⚠️ Missing/Simplified (From Original Plan)

1. **WebSocket** → Used polling instead
   - Simpler implementation
   - Good enough for POC
   - WebSocket would be better for production

2. **Database** → No persistence
   - Products: JSON file
   - Jobs: In-memory dict
   - Lost on restart
   - Need SQLite or PostgreSQL for production

3. **Queue System** → No Redis/Celery
   - Using Python asyncio + in-memory
   - Can't scale horizontally
   - Single server only

4. **State Management** → No Zustand
   - Using React useState
   - Fine for simple POC
   - Would need for complex app

5. **Custom Hooks** → Logic inline
   - No useCamera, useTryOn hooks
   - Less reusable
   - Harder to test

6. **Component Architecture** → Monolithic pages
   - No separate ProductCard, TryOnResult components
   - Everything in page files
   - Less maintainable

7. **Config System** → Hardcoded
   - No JSON config file
   - ENABLE_CUSTOM_PROMPT hardcoded in TryOn.tsx
   - Should be env var or config file

8. **AI Model** → Gemini instead of IDM-VTON
   - Original plan recommended Replicate's IDM-VTON
   - Using Gemini 2.5 Flash Image (user's choice)
   - Quality may vary, not specialized for VTON

9. **Deployment** → Not on cloud
   - Still local + ngrok
   - Need Vercel + Railway for production

10. **Testing** → None
    - No unit tests
    - No integration tests
    - No E2E tests
    - Manual testing only

11. **Documentation** → Minimal
    - No API.md
    - FastAPI auto-docs exist
    - README covers basics

12. **File Structure** → Simplified
    - No utils/ folder
    - No separate images.py router
    - Consolidated for speed

---

## 🔴 Critical Gaps (Will Cause Issues)

### 1. No Job Persistence
**Problem**: Jobs stored in-memory. Backend restart = all lost.
**Impact**: User submits job, backend restarts, job gone.
**Fix**: Use SQLite or PostgreSQL.

### 2. No Timeout Handling
**Problem**: Gemini API calls have no timeout.
**Impact**: If Gemini hangs, request never completes.
**Fix**: Add asyncio.wait_for() with 30s timeout.

### 3. No Error Fallback
**Problem**: If Gemini fails, no graceful recovery.
**Impact**: App shows error, user confused.
**Fix**: Catch exceptions, show user-friendly message, offer retry.

### 4. Path Resolution Issues
**Problem**: Garment image paths resolved incorrectly.
**Impact**: "No such file or directory" errors.
**Fix**: Already fixed with absolute paths (V1/frontend/public/products/).

### 5. No Rate Limiting
**Problem**: Can spam Gemini API, hit quota.
**Impact**: API blocked, demo fails.
**Fix**: Add rate limiter or queue.

### 6. No Request Validation
**Problem**: Can upload huge files, weird formats.
**Impact**: Memory issues, crashes.
**Fix**: Validate file size, type, dimensions.

### 7. No Job Cleanup
**Problem**: Old jobs never deleted.
**Impact**: Memory leak over time.
**Fix**: Add TTL, clean up jobs older than 1 hour.

### 8. No Result Caching
**Problem**: Same prompt + image = new API call.
**Impact**: Waste money, slower.
**Fix**: Cache results by hash.

---

## Technical Decisions Made

### Why Gemini Instead of IDM-VTON?
- User already had Gemini API key
- Faster to set up
- Good enough for POC demo
- IDM-VTON would need Replicate account + different API

### Why Polling Instead of WebSocket?
- Simpler to implement
- Easier to deploy
- Good enough for POC
- WebSocket would be better for production (real-time)

### Why In-Memory Jobs Instead of Database?
- Zero setup, no dependencies
- Fast for POC
- Acceptable for single-server demo
- Would need DB for production

### Why No Tests?
- Time constraint (demo tomorrow)
- POC phase, rapid iteration
- Manual testing sufficient for demo
- Would write tests for production

### Why Inline Components Instead of Separation?
- Faster to write
- Less files to manage
- Easier to see full flow
- Would refactor for production

---

## Known Bugs & Issues

### 1. Garment Path Resolution (FIXED)
- Was looking in backend/frontend/public/products/
- Fixed to use V1/frontend/public/products/

### 2. ngrok Host Blocking (FIXED)
- Vite was rejecting ngrok domain
- Fixed by adding to allowedHosts in vite.config.ts

### 3. Local Network Not Accessible (PARTIALLY FIXED)
- Needed explicit --host 0.0.0.0
- Now works but some networks have AP isolation
- Fallback: use ngrok

### 4. Result Image URL Wrong (NEEDS FIX)
- Sometimes shows full system path
- Should be relative /uploads/filename.jpg
- Check tryon.py result URL construction

### 5. Error Toasts Too Fast (NEEDS FIX)
- Errors disappear before user can read
- Need longer timeout or persistent error display

### 6. No Loading State on Regenerate (NEEDS FIX)
- Click regenerate, no immediate feedback
- Should show loading immediately

---

## Architecture Overview

```
Frontend (React)
  ↓ HTTP POST /api/tryon/start
Backend (FastAPI)
  ↓ Save image, create job
  ↓ Async: process_tryon()
  ↓ Load person + garment images
  ↓ Call gemini_service.generate_tryon()
Gemini API (2.5 Flash Image)
  ↓ Generate try-on image
  ↓ Return image data
Backend
  ↓ Save result image
  ↓ Update job status
Frontend
  ↓ Poll GET /api/tryon/status/{job_id}
  ↓ Display result when completed
```

---

## Data Flow

1. User clicks "Try On" → Camera opens
2. User captures photo → Blob created
3. Frontend POST /api/tryon/start
   - Form data: product_id, person_image (blob), custom_prompt
4. Backend creates job, saves image
   - Job ID: UUID
   - Status: "pending"
   - Image: uploads/{job_id}_person.jpg
5. Backend starts async processing
   - Status: "processing"
   - Load garment image from products/
   - Call Gemini with both images + prompt
6. Gemini generates image (10-30s)
   - Returns PNG data
   - Backend saves to uploads/{job_id}_result.jpg
7. Job status updated to "completed"
8. Frontend polls every 2s
   - GET /api/tryon/status/{job_id}
   - Sees status: "completed"
   - Gets result_image_url
9. Display result image

---

## Gemini Integration Notes

### Model: gemini-2.5-flash-image
- Supports image generation (not just understanding)
- Takes multiple images as input
- Returns image data in response.parts[].inline_data
- Response format: PNG binary data

### Prompt Structure
```
Generate a photorealistic image showing this person wearing the garment.

Requirements:
- Keep person's features exactly as shown
- Dress them in the garment
- Ensure proper fit and draping
- Maintain garment colors/patterns
- Professional lighting

[Optional: Custom styling instructions]
```

### Response Handling
```python
for part in response.parts:
    if hasattr(part, 'inline_data') and part.inline_data.data:
        # Got image data
        image_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type  # "image/png"
```

### Limitations
- Not specialized for VTON (general image model)
- Quality varies based on input images
- Can hallucinate details
- Better with clear, well-lit photos
- May struggle with complex patterns

---

## Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=         # Google AI API key
MOCK_MODE=False         # True = fake results
MOCK_DELAY=3            # Seconds for mock delay
DEBUG=True              # FastAPI debug mode
HOST=0.0.0.0            # Listen on all interfaces
PORT=8000               # Backend port
CORS_ORIGINS=           # Allowed origins (comma-separated)
MAX_UPLOAD_SIZE=10485760 # 10MB
UPLOAD_DIR=uploads      # Where to save images
```

### Frontend (hardcoded in TryOn.tsx)
```typescript
const ENABLE_CUSTOM_PROMPT = true; // Show prompt input
```

---

## TODO for Production

### High Priority
1. [ ] Add database (SQLite → PostgreSQL)
2. [ ] Add timeout to Gemini calls (30s)
3. [ ] Add error fallback with retry logic
4. [ ] Add job cleanup (TTL: 1 hour)
5. [ ] Add request validation (file size, type)
6. [ ] Add rate limiting
7. [ ] Add proper logging (not just print)
8. [ ] Add health check endpoint for jobs

### Medium Priority
9. [ ] Separate components (ProductCard, etc.)
10. [ ] Create custom hooks (useCamera, useTryOn)
11. [ ] Add unit tests (backend services)
12. [ ] Add E2E tests (Playwright/Cypress)
13. [ ] Add WebSocket for real-time updates
14. [ ] Add result caching
15. [ ] Add image optimization (compress uploads)
16. [ ] Add metrics/analytics

### Low Priority
17. [ ] Add user accounts/auth
18. [ ] Add saved results
19. [ ] Add social sharing
20. [ ] Add shopping cart
21. [ ] Add payment integration
22. [ ] Switch to IDM-VTON (better quality)

---

## Deployment Notes

### Local Development
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Works well for testing

### Network Access
- Backend on 0.0.0.0:8000 (accessible from network)
- Frontend on 0.0.0.0:5173 (accessible from network)
- Local IP: 192.168.1.35
- Works if no AP isolation

### ngrok Tunnel
- Running on port 5173
- URL: https://proapostolic-unputatively-neil.ngrok-free.dev
- Free tier, URL changes on restart
- Has warning page (click "Visit Site")

### Production (Not Done Yet)
- Frontend: Vercel (free tier)
- Backend: Railway or Render (free tier)
- Need to:
  1. Push to GitHub
  2. Connect Vercel to repo
  3. Connect Railway to repo
  4. Set env vars
  5. Deploy
  6. Update CORS
  7. Test

---

## Performance Notes

### Timings
- Camera open: <1s
- Photo capture: instant
- Upload to backend: <1s (local)
- Gemini generation: 10-30s (varies)
- Result polling: 2s intervals
- Total: ~15-35s per try-on

### Bottlenecks
- Gemini API is slowest part
- Image upload size (compress?)
- No caching (repeat requests slow)

### Optimizations Done
- Async processing (non-blocking)
- Progress bar (perceived speed)
- Polling interval (not too aggressive)

### Optimizations Needed
- Image compression before upload
- Result caching (same input = cached output)
- CDN for product images
- Lazy loading catalog

---

## Security Notes (For Production)

### Current Issues
- No authentication
- No authorization
- No rate limiting
- No input validation
- Uploads not sanitized
- API key in plain text
- CORS allows all origins
- No HTTPS enforcement

### Production Needs
- Add JWT auth
- Validate all inputs
- Sanitize file uploads
- Use secrets manager for API keys
- Restrict CORS to specific domains
- Enforce HTTPS
- Add rate limiting (per IP/user)
- Add CSP headers

---

## Debugging Tips

### Backend Not Starting
```bash
# Check if port is in use
lsof -i :8000

# Kill process
kill -9 <PID>

# Check logs
tail -f /tmp/backend_output.log
```

### Frontend Not Accessible on Phone
```bash
# Check if listening on all interfaces
lsof -i :5173

# Should see: *:5173 (not 127.0.0.1:5173)

# Restart with explicit host
npm run dev -- --host 0.0.0.0
```

### Gemini API Errors
```bash
# Test API key
curl https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY

# Check quota
# Go to: https://ai.google.dev/

# Test in Python
python3 -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print(list(genai.list_models()))"
```

### Job Not Completing
```bash
# Check job status
curl http://localhost:8000/api/tryon/status/{JOB_ID}

# Check backend logs
# Look for exceptions in Gemini service
```

---

## Future Improvements

### Short Term (Next Session)
- Fix result image URL issue
- Add timeout to Gemini calls
- Make error toasts stay longer
- Add loading state on regenerate
- Test extensively on demo phone

### Medium Term (Post-Demo)
- Add database for job persistence
- Implement proper error handling
- Add request validation
- Deploy to production
- Write documentation

### Long Term (If Continuing)
- Switch to IDM-VTON for better quality
- Add user accounts and history
- Add saved results and favorites
- Implement shopping cart
- Add payment integration
- Build admin panel

---

**Last Updated**: 2026-03-28 03:30 AM
**Status**: V0 working, needs polish before demo
**Next**: Fix critical bugs, test on phone, practice demo
