# Railway Deployment Guide for Email Security Analyzer

## Overview
This guide will help you deploy your Flask backend on Railway.

---

## Step 1: Prepare Your Repository ✅

Your repo now has:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway configuration
- ✅ `.env.example` - Environment variables template
- ✅ Updated `app.py` - Production-ready Flask app

---

## Step 2: Create a Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Create New Project"**
3. Sign up with GitHub account (easier!)

---

## Step 3: Deploy to Railway

### Option A: Connect GitHub (Recommended)
1. Click **"Create New Project"**
2. Select **"Deploy from GitHub"**
3. Select your repository: `Email_security-Analyser-using-Mimecast`
4. Railway will auto-detect Python and use your Procfile
5. Click **"Deploy"** ✅

### Option B: Connect with Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

---

## Step 4: Set Environment Variables

After deployment, Railway needs your Mimecast credentials:

1. Go to your Railway project dashboard
2. Click on your deployment/service
3. Go to **"Variables"** tab
4. Add these environment variables:

```
FLASK_ENV=production
MIMECAST_CLIENT_ID=<your_client_id>
MIMECAST_CLIENT_SECRET=<your_client_secret>
MIMECAST_BASE_URL=https://api.mimecast.com
```

⚠️ **Important**: Get these from your Mimecast account

---

## Step 5: Get Your Backend URL

1. In Railway dashboard, find your project
2. Go to **"Domains"** section
3. Copy the auto-generated URL (looks like `https://project-name-prod.railway.app`)

Your backend API will be available at:
- `https://your-railway-url.railway.app/`
- `https://your-railway-url.railway.app/api/token`
- `https://your-railway-url.railway.app/api/search`

---

## Step 6: Update Frontend API Calls

Update your frontend to use the Railway backend URL:

```javascript
// Example: In your frontend code
const BACKEND_URL = "https://your-railway-url.railway.app";

// Instead of localhost:5000
const response = await fetch(`${BACKEND_URL}/api/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        clientId: "...",
        clientSecret: "...",
        baseUrl: "..."
    })
});
```

---

## Step 7: Test Your Deployment

### Health Check
```bash
curl https://your-railway-url.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test Token Endpoint
```bash
curl -X POST https://your-railway-url.railway.app/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "your_id",
    "clientSecret": "your_secret",
    "baseUrl": "https://api.mimecast.com"
  }'
```

---

## Step 8: Monitor Logs

1. In Railway dashboard, click your service
2. Go to **"Logs"** tab
3. Watch real-time deployment and application logs

---

## Troubleshooting

### Issue: Port Already in Use
**Fix**: Railway auto-assigns PORT via environment variable. Your app now uses this.

### Issue: CORS Errors
**Fix**: Your Flask app has Flask-CORS enabled. Frontend can call the API.

### Issue: Environment Variables Not Working
**Fix**: Restart your deployment after adding variables:
1. Go to **"Deployments"** tab
2. Click the deployment
3. Click **"Redeploy"**

### Issue: Import Errors
**Fix**: Make sure `requirements.txt` is in the `backend/` directory

---

## Final Architecture

```
Your Frontend (Vercel)
    ↓
    ↓ API Calls
    ↓
Your Backend (Railway)
    ↓
    ↓ Mimecast API
    ↓
Mimecast API
```

---

## Costs

- **Railway**: Free tier available (100GB memory/month)
- **Vercel Frontend**: Free tier available
- **Mimecast API**: Your existing account

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy to Railway
3. ✅ Set environment variables
4. ✅ Update frontend with new API URL
5. ✅ Test end-to-end

---

## Need Help?

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Flask Docs: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- Mimecast API Docs: [mimecast.com/api](https://mimecast.com/api)

Good luck! 🚀
