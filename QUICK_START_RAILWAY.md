# 🚂 Quick Start: Deploy to Railway

Your repository is now configured for Railway deployment! Here's how to deploy in 5 minutes.

---

## ✅ What Was Done

I've set up your repository with:

- ✅ `backend/railway.toml` - Railway configuration
- ✅ `backend/Procfile` - Start command
- ✅ `backend/runtime.txt` - Python 3.11 runtime
- ✅ `backend/requirements.txt` - Updated with uvicorn for production
- ✅ `backend/.env.example` - Environment variables template
- ✅ `backend/src/dynamic_tools/api/app.py` - Added CORS middleware
- ✅ `.gitignore` - Updated to allow .env.example files
- ✅ Complete deployment documentation

---

## 🚀 Deploy Now (2 Options)

### Option A: Deploy via GitHub (Easiest - 3 minutes)

1. **Push your code to GitHub:**
   ```bash
   git push origin feat/merge_backend
   ```

2. **Go to [railway.app](https://railway.app) and login**

3. **Click "Start a New Project" → "Deploy from GitHub repo"**

4. **Select your `mcp-factor` repository**

5. **Configure deployment:**
   - Click "Configure" 
   - Set **Root Directory** to: `/backend`
   - Click "Add variables"

6. **Add Environment Variables:**
   - `OPENAI_API_KEY` = your OpenAI API key
   - `ALPHA_VANTAGE_API_KEY` = `demo` (or your key)

7. **Click "Deploy"** 🎉

8. **Get your URL:**
   - Go to "Settings" → "Networking" → "Generate Domain"
   - You'll get: `https://your-app.up.railway.app`

---

### Option B: Deploy via CLI (Quick - 5 minutes)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Navigate to backend
cd backend

# 4. Initialize Railway project
railway init

# 5. Add environment variables
railway variables set OPENAI_API_KEY=your-actual-key-here
railway variables set ALPHA_VANTAGE_API_KEY=demo

# 6. Deploy!
railway up

# 7. Get your URL
railway status
```

---

## 🧪 Test Your Deployment

Once deployed, test these endpoints:

```bash
# Replace with your actual Railway URL
BACKEND_URL="https://your-app.up.railway.app"

# Health check
curl $BACKEND_URL/health

# Expected: {"status":"healthy","service":"llm-http-service"}

# Root info
curl $BACKEND_URL/

# API Documentation (open in browser)
open $BACKEND_URL/docs
```

---

## 🔗 Connect Frontend to Backend

After backend is deployed:

### 1. Create frontend environment file

In your **project root** (not in backend), create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### 2. Deploy frontend to Vercel

```bash
# Option 1: Via CLI
vercel
vercel env add NEXT_PUBLIC_API_URL production
# Enter your Railway backend URL
vercel --prod

# Option 2: Via GitHub
# Push to GitHub, then import project on vercel.com
```

---

## 📋 Deployment Checklist

Backend:
- [ ] Push code to GitHub
- [ ] Deploy to Railway (Option A or B above)
- [ ] Add `OPENAI_API_KEY` environment variable
- [ ] Add `ALPHA_VANTAGE_API_KEY` environment variable
- [ ] Test `/health` endpoint
- [ ] Copy your Railway URL

Frontend:
- [ ] Create `.env.local` with `NEXT_PUBLIC_API_URL`
- [ ] Deploy to Vercel
- [ ] Test frontend can reach backend
- [ ] Celebrate! 🎉

---

## 💡 Pro Tips

### Enable Automatic Deployments

Railway auto-deploys when you push to GitHub (if you used Option A).

For manual control:
```bash
cd backend
railway up
```

### View Logs

```bash
railway logs
```

Or in Railway dashboard → Your service → Deployments tab

### Add Custom Domain

Railway dashboard → Settings → Networking → Add custom domain

---

## 🐛 Troubleshooting

### "No module named 'src'" error

Solution: Ensure Railway root directory is set to `/backend`
- Railway dashboard → Settings → Root Directory → `/backend`

### CORS errors in frontend

Solution: Your frontend domain needs to be in the CORS allowlist.

Edit `backend/src/dynamic_tools/api/app.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://*.vercel.app",
    "https://your-actual-frontend.vercel.app",  # Add this
],
```

Then redeploy:
```bash
cd backend
railway up
```

### Environment variables not working

Check variables are set:
```bash
railway variables
```

Add missing ones:
```bash
railway variables set OPENAI_API_KEY=your-key
```

---

## 📚 Full Documentation

- **Detailed Railway Guide**: [`backend/RAILWAY_DEPLOYMENT.md`](backend/RAILWAY_DEPLOYMENT.md)
- **Full Deployment Guide**: [`DEPLOYMENT.md`](DEPLOYMENT.md)
- **Vercel Deployment**: [`backend/VERCEL_DEPLOYMENT.md`](backend/VERCEL_DEPLOYMENT.md)

---

## 💰 Cost

- **Railway Free Trial**: $5 in credits
- **Typical monthly cost**: $5-10 for light traffic
- **Vercel**: FREE for hobby projects

---

## ✅ You're Ready!

Your repository is configured and ready to deploy. Choose Option A or B above and you'll be live in minutes!

Questions? Check the full documentation or Railway's support at [docs.railway.app](https://docs.railway.app)

Happy deploying! 🚀

