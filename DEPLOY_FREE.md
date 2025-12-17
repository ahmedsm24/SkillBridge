# Free Deployment Guide for SkillBridge

Deploy SkillBridge completely free using:
- **MongoDB Atlas** (Free 512MB database)
- **Render** (Free backend hosting)
- **Vercel** (Free frontend hosting)

Total Cost: **$0/month**

---

## Step 1: Set Up MongoDB Atlas (5 minutes)

### 1.1 Create Account
1. Go to [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up with Google or email

### 1.2 Create Free Cluster
1. Click **"Build a Database"**
2. Select **M0 FREE** tier
3. Choose provider: **AWS**
4. Choose region: **Closest to you** (e.g., us-east-1)
5. Cluster name: `skillbridge-cluster`
6. Click **"Create"**

### 1.3 Create Database User
1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Authentication: **Password**
4. Username: `skillbridge`
5. Password: **Generate a secure password** (save this!)
6. Role: **Read and write to any database**
7. Click **"Add User"**

### 1.4 Allow Network Access
1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (adds 0.0.0.0/0)
4. Click **"Confirm"**

### 1.5 Get Connection String
1. Go to **Database** (left sidebar)
2. Click **"Connect"** on your cluster
3. Select **"Connect your application"**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://skillbridge:<password>@skillbridge-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add database name before `?`:
   ```
   mongodb+srv://skillbridge:YOUR_PASSWORD@skillbridge-cluster.xxxxx.mongodb.net/skillbridge?retryWrites=true&w=majority
   ```

**Save this connection string!**

---

## Step 2: Push Code to GitHub (2 minutes)

If not already on GitHub:

```bash
cd /Users/ahmed/Desktop/larsonwork

# Initialize git (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - SkillBridge"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/skillbridge.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy Backend to Render (5 minutes)

### 3.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### 3.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your `skillbridge` repo

### 3.3 Configure Service
- **Name**: `skillbridge-api`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Docker`
- **Instance Type**: **Free**

### 3.4 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `USE_MONGODB` | `true` |
| `MONGODB_URI` | `mongodb+srv://skillbridge:YOUR_PASSWORD@...` (your connection string) |
| `OPENAI_API_KEY` | `sk-...` (your OpenAI key, optional) |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | `https://skillbridge.vercel.app` (update after Vercel deploy) |

### 3.5 Deploy
1. Click **"Create Web Service"**
2. Wait for build (3-5 minutes)
3. Copy your URL: `https://skillbridge-api.onrender.com`

---

## Step 4: Deploy Frontend to Vercel (3 minutes)

### 4.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 4.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Select the `skillbridge` repo

### 4.3 Configure Project
- **Framework Preset**: Next.js
- **Root Directory**: `frontend`

### 4.4 Add Environment Variable
Click **"Environment Variables"**:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://skillbridge-api.onrender.com` (your Render URL) |

### 4.5 Deploy
1. Click **"Deploy"**
2. Wait for build (1-2 minutes)
3. Your app is live at: `https://skillbridge-YOUR_NAME.vercel.app`

---

## Step 5: Update CORS (1 minute)

Go back to Render:
1. Open your web service
2. Go to **Environment**
3. Update `ALLOWED_ORIGINS` to your Vercel URL:
   ```
   https://skillbridge-YOUR_NAME.vercel.app
   ```
4. Click **"Save Changes"** (auto-redeploys)

---

## Done! Your App is Live

- **Frontend**: `https://skillbridge-YOUR_NAME.vercel.app`
- **Backend API**: `https://skillbridge-api.onrender.com`
- **API Docs**: `https://skillbridge-api.onrender.com/docs`

---

## Free Tier Limits

| Service | Limit | Note |
|---------|-------|------|
| **MongoDB Atlas** | 512 MB storage | Enough for thousands of resumes |
| **Render** | 750 hours/month | Sleeps after 15 min inactivity |
| **Vercel** | 100 GB bandwidth | More than enough |

### Note on Render Free Tier
The backend will "sleep" after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up. This is normal for free tier.

---

## Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS as instructed

### Render
1. Go to Service Settings → Custom Domains
2. Add your domain
3. Update DNS as instructed

---

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify MONGODB_URI is correct
- Ensure MongoDB user has correct permissions

### Frontend can't connect to API
- Check NEXT_PUBLIC_API_URL is correct
- Check ALLOWED_ORIGINS includes your Vercel domain
- Check browser console for CORS errors

### MongoDB connection fails
- Verify IP whitelist includes 0.0.0.0/0
- Check username/password are correct
- Ensure connection string includes database name

---

## Support

- MongoDB Atlas: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- Render: [render.com/docs](https://render.com/docs)
- Vercel: [vercel.com/docs](https://vercel.com/docs)

