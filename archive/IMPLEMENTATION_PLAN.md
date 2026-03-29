# VTON - Virtual Try-On Implementation Plan

## Project Overview

**Purpose**: Demo POC for potential clients showcasing AI-powered virtual try-on for fashion e-commerce.

**Core Concept**: A fashion e-commerce site where users can click "Try On" on any product, take a photo with their camera, optionally add styling prompts, and receive an AI-generated image of themselves wearing the garment.

---

## Requirements Summary

### Functional Requirements
1. **E-commerce UI**: Catalog of 10-20 fashion products with product pages
2. **Try-On Flow**:
   - Product page → "Try On" button
   - Camera access (front and rear cameras)
   - Photo capture
   - Optional: Custom styling prompt input (config-toggleable)
   - AI generation of try-on image
   - Result display with notification
3. **Follow-up Edits**: Ability to refine/re-generate with different prompts
4. **Async Processing**: Handle 5-20 second generation times gracefully
5. **Notifications**: Alert user when image is ready

### Non-Functional Requirements
- **Mobile-First**: Must work flawlessly on phones (primary demo device)
- **Camera Access**: Both front and rear cameras
- **Error Handling**: Robust error handling throughout
- **UX**: No infinite waits, loading states, progress indicators
- **Performance**: Asynchronous processing with background generation
- **Responsive**: Works across devices but optimized for mobile

---

## Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (SPA)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Product    │  │   Camera     │  │   Try-On     │      │
│  │   Catalog    │→ │   Capture    │→ │   Results    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    REST API / WebSocket
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Backend API Server                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Products   │  │    Image     │  │    Queue     │      │
│  │     API      │  │   Upload     │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    AI Model Integration
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Virtual Try-On AI Service                       │
│         (Google Gemini / Replicate / Custom)                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Product Browse**: User browses catalog → Selects product
2. **Initiate Try-On**: Clicks "Try On" → Camera UI opens
3. **Capture**: User takes photo (front/rear camera)
4. **Submit**: Photo + Product + Optional Prompt → Backend
5. **Process**: Backend queues job → Calls AI API → Polls/webhooks for result
6. **Notify**: Backend notifies frontend (WebSocket/polling) when ready
7. **Display**: Show result with edit options
8. **Iterate**: User can submit new prompts for refinement

---

## Tech Stack Recommendations

### Frontend
**Framework**: **React + Vite** (or Next.js for SSR/SSG benefits)
- Fast dev experience, modern tooling
- Excellent mobile support
- Large ecosystem

**UI Library**: **Tailwind CSS + shadcn/ui**
- Rapid prototyping
- Mobile-responsive out of the box
- Professional look with minimal effort

**State Management**: **Zustand** or **React Context**
- Simple, lightweight for POC
- Easy async state handling

**Camera Library**: **react-camera-pro** or native **MediaDevices API**
- Access to front/rear cameras
- Mobile-optimized
- Good browser support

**Notifications**: **React Hot Toast** or **Sonner**
- Non-intrusive notifications
- Mobile-friendly

**HTTP Client**: **Axios** or **Fetch API**
- Simple async requests

**WebSocket** (optional): **Socket.io-client**
- For real-time notifications when image is ready

### Backend
**Framework**: **Node.js + Express** or **Python + FastAPI**

**Recommendation: FastAPI (Python)**
- Faster development for AI integrations
- Excellent async support
- Auto-generated API docs
- Easy integration with Python AI libraries
- Type safety with Pydantic

**File Storage**:
- **Local filesystem** (for POC)
- Or **AWS S3 / Cloudflare R2** (if deploying publicly)

**Queue System** (optional):
- **Redis + Bull** (Node.js) or **Celery** (Python)
- For async job processing
- Not critical for POC but nice to have

**Database**: **SQLite** or **PostgreSQL**
- SQLite for simplicity (file-based, zero config)
- PostgreSQL if scaling or deployed

---

## AI Model Selection for Virtual Try-On

### Research Summary

**Current VTON State-of-the-Art (March 2026):**

1. **IDM-VTON** (Replicate)
   - State-of-the-art results
   - Available via Replicate API
   - ~10-30s generation time
   - Cost: ~$0.05-0.10 per generation
   - ✅ **RECOMMENDED**

2. **Google Gemini Vision** (Gemini 2.0 Flash)
   - Mentioned as decent in requirements
   - Can do virtual try-on via prompting
   - Fast (~2-5s)
   - Less specialized than dedicated VTON models
   - Good for quick iteration

3. **Kolors Virtual Try-On** (Replicate)
   - High quality results
   - ~15-25s generation time
   - Good garment detail preservation

4. **SDXL + ControlNet + IP-Adapter**
   - DIY approach with more control
   - Requires more setup
   - Can self-host

**Recommendation for Demo:**
- **Primary**: IDM-VTON via Replicate API (best quality)
- **Fallback**: Gemini 2.0 Flash (faster, cheaper, good enough)
- **Config**: Allow switching between models via environment variable

---

## Implementation Plan

### Phase 1: Project Setup & Architecture (2-3 hours)
- [ ] Initialize Git repository
- [ ] Setup frontend (React + Vite + Tailwind)
- [ ] Setup backend (FastAPI + Python)
- [ ] Define folder structure
- [ ] Setup environment variables
- [ ] Create config system for toggleable features

### Phase 2: Backend Core (3-4 hours)
- [ ] Product catalog API (static JSON for POC)
- [ ] Image upload endpoint
- [ ] AI integration layer (Replicate/Gemini SDK)
- [ ] Job queue/tracking system
- [ ] WebSocket or polling endpoint for status
- [ ] Error handling middleware
- [ ] CORS configuration for mobile testing

### Phase 3: Frontend Core (4-5 hours)
- [ ] Product catalog page (grid layout)
- [ ] Product detail page
- [ ] Camera component (front/rear toggle)
- [ ] Photo capture & preview
- [ ] Optional prompt input (config-based)
- [ ] Loading states & progress indicators
- [ ] Result display component
- [ ] Edit/regenerate flow

### Phase 4: Integration & Polish (3-4 hours)
- [ ] Connect frontend to backend APIs
- [ ] Implement async job polling/WebSocket
- [ ] Notification system
- [ ] Mobile responsive testing
- [ ] Error handling & edge cases
- [ ] Loading states optimization
- [ ] Camera permissions handling

### Phase 5: Sample Data & Assets (1-2 hours)
- [ ] Create 10-20 product entries
- [ ] Source product images (free stock photos)
- [ ] Write product descriptions
- [ ] Test data validation

### Phase 6: Testing & Demo Prep (2-3 hours)
- [ ] Mobile device testing (iPhone/Android)
- [ ] Camera functionality testing
- [ ] End-to-end flow testing
- [ ] Error scenario testing
- [ ] Performance testing
- [ ] Demo script preparation

**Total Estimated Time**: 15-21 hours

---

## Deployment Strategy

### Option 1: Vercel (Frontend) + Railway/Render (Backend) ✅ RECOMMENDED
**Pros:**
- Professional, fast deployment
- Free tiers available
- SSL/HTTPS out of the box
- Good mobile performance
- Persistent URLs

**Cons:**
- Requires separate services
- Slight complexity in CORS setup

**Steps:**
1. Deploy frontend to Vercel (connect GitHub repo)
2. Deploy backend to Railway or Render
3. Update frontend env vars with backend URL
4. Test on mobile devices

### Option 2: NGROK (Tunnel) + Local Dev
**Pros:**
- Zero deployment complexity
- Instant testing
- Full local control

**Cons:**
- Requires laptop to be running during demo
- Potential network issues
- URL changes each restart (unless paid)

**Steps:**
1. Run backend locally
2. Run frontend locally
3. NGROK tunnel to frontend port
4. Update backend CORS for NGROK URL
5. Share NGROK URL for demo

### Option 3: Single Server Deployment (Docker)
**Pros:**
- Single deployment unit
- Easier to manage

**Cons:**
- More complex setup
- Overkill for POC

**Recommendation**: **Option 1 (Vercel + Railway)** for professional demo, **Option 2 (NGROK)** if time-constrained.

---

## Configuration System

Create a `config.json` or environment variables for:

```json
{
  "features": {
    "enableCustomPrompts": true,
    "enableNotifications": true,
    "enableEditFlow": true
  },
  "ai": {
    "provider": "replicate",  // "replicate" | "gemini"
    "model": "idm-vton"
  },
  "demo": {
    "mockMode": false,  // Use fake generation for testing
    "mockDelay": 5000
  }
}
```

---

## Demo Considerations

### Critical Success Factors
1. **Camera works flawlessly** on demo phone
2. **Fast feedback** - show progress, not blank screens
3. **Error recovery** - if AI fails, graceful fallback
4. **Network resilience** - handle slow connections
5. **Professional look** - polished UI even as POC

### Demo Script Outline
1. **Browse Products** (15 sec)
   - Show catalog, scroll through products

2. **Select Product** (5 sec)
   - Click on a shirt/dress

3. **Initiate Try-On** (5 sec)
   - Hit "Try On" button

4. **Capture Photo** (10 sec)
   - Camera opens, take selfie

5. **Optional: Add Prompt** (10 sec)
   - "Make it look casual" or "Add a jacket"

6. **Show Processing** (15-30 sec)
   - Loading animation, progress indicator
   - Notification when ready

7. **Reveal Result** (15 sec)
   - Show generated image
   - Highlight quality/realism

8. **Edit Flow** (optional, 20 sec)
   - Click edit, change prompt
   - Show regeneration

**Total Demo Time**: ~2-3 minutes per try-on

### Backup Plans
- **Pre-generated samples** as fallback if live generation fails
- **Mock mode** for offline demo
- **Multiple test accounts** with different photos ready

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| AI API fails/slow | Fallback to secondary model (Gemini), mock mode |
| Camera doesn't work on phone | Test on multiple devices beforehand, use uploaded images |
| Network issues during demo | Deploy with CDN, test on mobile network, have offline mode |
| Generation takes too long | Set max timeout, show engaging loading animation |
| Poor quality results | Curate good sample images, test multiple models |
| CORS issues on mobile | Configure properly, test cross-origin scenarios |

---

## File Structure Proposal

```
V1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductDetail.tsx
│   │   │   ├── Camera.tsx
│   │   │   ├── TryOnResult.tsx
│   │   │   └── PromptInput.tsx
│   │   ├── pages/
│   │   │   ├── Catalog.tsx
│   │   │   ├── Product.tsx
│   │   │   └── TryOn.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   ├── useCamera.ts
│   │   │   └── useTryOn.ts
│   │   ├── config.ts
│   │   └── App.tsx
│   ├── public/
│   │   └── products/
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   └── product.py
│   │   ├── routers/
│   │   │   ├── products.py
│   │   │   ├── tryon.py
│   │   │   └── images.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── replicate_service.py
│   │   │   └── gemini_service.py
│   │   └── utils/
│   ├── data/
│   │   └── products.json
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   └── API.md
├── IMPLEMENTATION_PLAN.md
├── context.txt
└── README.md
```

---

## Next Steps

1. **Review this plan** - Discuss any concerns, changes, preferences
2. **Confirm tech stack** - Agree on React/FastAPI, Replicate vs Gemini
3. **Confirm deployment** - Vercel or NGROK?
4. **Set priorities** - Which features are must-have vs nice-to-have?
5. **Get API keys** - Replicate and/or Google AI API keys ready
6. **Start implementation** - Begin with Phase 1

---

## Questions for Discussion

1. **AI Provider**: Do you have a preference between Replicate (IDM-VTON) vs Google Gemini? (Quality vs Speed trade-off)
2. **Deployment**: Vercel + Railway (professional) or NGROK (quick)? When is the demo?
3. **Product Catalog**: Do you have specific fashion items in mind, or should I source generic fashion images?
4. **Prompt Feature**: Should the custom prompt input be enabled by default, or hidden unless toggled?
5. **Budget**: Any constraints on API costs? (Replicate ~$0.05-0.10 per generation)
6. **Testing**: What phone will be used for demo? (iPhone/Android, specific model)
7. **Mock Data**: Should we prepare pre-generated samples as backup?

---

## Conclusion

This is a well-scoped POC that can be delivered in 15-20 hours of focused work. The architecture is simple but robust, mobile-first, and designed for a smooth demo experience. The async processing, notifications, and error handling will make it feel professional despite being a POC.

Ready to discuss and then implement! 🚀
