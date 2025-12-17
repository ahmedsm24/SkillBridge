# How to Deploy and Use the Application

## Does It Need Internet/WiFi?

**Yes, this application requires an internet connection** (WiFi, ethernet, or mobile data) because:

1. **It's a web application** - Runs in a web browser
2. **Backend API** - Needs to communicate with the server
3. **AI Features** - Uses OpenAI API (requires internet)
4. **Database** - Stored on a server (not locally)

**You cannot use it offline.** Users need internet access to:
- Access the website
- Upload resumes
- Generate training modules
- View results

---

## Quick Deployment Guide (Easiest Method)

### Prerequisites
- GitHub account (free)
- Railway account (free tier available) - for backend
- Vercel account (free) - for frontend
- OpenAI API key (optional but recommended)

### Step 1: Prepare Your Code

```bash
# Make sure you're in the project directory
cd /Users/ahmed/Desktop/larsonwork

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Railway

1. **Go to Railway.app**
   - Sign up/login (free tier available)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Backend**
   - Railway will detect it's a Python project
   - Set the root directory to: `backend`
   - Add these environment variables:
     ```
     DATABASE_URL=postgresql://... (Railway provides this automatically)
     OPENAI_API_KEY=sk-your-key-here (get from openai.com)
     SECRET_KEY=generate-random-string-here
     ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
     ```

3. **Add PostgreSQL Database**
   - In Railway project, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

4. **Deploy**
   - Railway will automatically deploy
   - Copy the backend URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend to Vercel

1. **Go to Vercel.com**
   - Sign up/login (free)
   - Click "Add New Project"
   - Import your GitHub repository

2. **Configure Frontend**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Add environment variable:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```
   - Click "Deploy"

3. **Get Your Frontend URL**
   - Vercel will give you a URL like: `https://your-app.vercel.app`

### Step 4: Update Backend CORS

1. Go back to Railway
2. Update `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-app.vercel.app
   ```
3. Redeploy backend

### Step 5: Test Your Application

1. Open your Vercel URL in a browser
2. Try uploading a resume
3. Test the full workflow

---

## Alternative: Deploy to Your Own Server/VPS

If you want to host it yourself:

### Option A: Using Docker (Easiest)

```bash
# 1. Get a VPS (DigitalOcean, Linode, AWS EC2, etc.)
# 2. SSH into your server
ssh user@your-server-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Install Docker Compose
sudo apt-get install docker-compose

# 5. Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 6. Create .env file
cat > .env << EOF
DB_PASSWORD=your_secure_password_here
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://your-server-ip:3000
EOF

# 7. Start services
docker-compose up -d

# 8. Access your application
# Backend: http://your-server-ip:8000
# Frontend: You'll need to build and serve it separately
```

### Option B: Manual Installation

```bash
# 1. Install Python 3.11
sudo apt-get update
sudo apt-get install python3.11 python3-pip

# 2. Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 3. Create database
sudo -u postgres psql
CREATE DATABASE resume_training;
CREATE USER resume_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE resume_training TO resume_user;
\q

# 4. Set up backend
cd backend
pip install -r requirements.txt

# 5. Set environment variables
export DATABASE_URL=postgresql://resume_user:your_password@localhost:5432/resume_training
export OPENAI_API_KEY=sk-your-key-here
export SECRET_KEY=your-secret-key

# 6. Run backend
uvicorn src.main:app --host 0.0.0.0 --port 8000

# 7. Set up frontend (in another terminal)
cd frontend
npm install
npm run build
npm start
```

---

## How Users Will Use It

### For End Users (Your Customers)

1. **They need internet connection** (WiFi, mobile data, etc.)

2. **Open the website**:
   - Go to your Vercel URL (e.g., `https://your-app.vercel.app`)
   - Or your custom domain if you set one up

3. **Use the application**:
   - Upload resume (PDF or text file)
   - Enter job description
   - View gap analysis
   - Generate and view training modules

4. **No installation needed** - It's a web app, works in any browser

### Access Methods

- **Desktop/Laptop**: Open in Chrome, Firefox, Safari, Edge
- **Mobile/Tablet**: Open in mobile browser
- **Any device with internet**: Works anywhere with internet access

---

## Setting Up a Custom Domain (Optional)

### For Backend (Railway)

1. In Railway project, go to "Settings" → "Domains"
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` to include your domain

### For Frontend (Vercel)

1. In Vercel project, go to "Settings" → "Domains"
2. Add your domain (e.g., `yourdomain.com`)
3. Update DNS records as instructed
4. Update `NEXT_PUBLIC_API_URL` to your backend domain

---

## Testing Locally (Development)

If you want to test on your computer first:

```bash
# Terminal 1: Start Backend
cd backend
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./resume_training.db
export OPENAI_API_KEY=sk-your-key-here
uvicorn src.main:app --reload

# Terminal 2: Start Frontend
cd frontend
npm install
npm run dev

# Open browser: http://localhost:3000
```

**Note**: This only works on your computer. Others can't access it unless they're on the same network and you configure it.

---

## Cost Estimate

### Free Tier (Good for Testing)
- **Railway**: $5/month free credit (usually enough for small apps)
- **Vercel**: Free tier (generous limits)
- **OpenAI API**: Pay per use (~$0.002 per request)
- **Total**: ~$5-10/month for small usage

### Production (Many Users)
- **Railway**: $20-50/month depending on usage
- **Vercel**: Free tier usually sufficient
- **OpenAI API**: Varies by usage
- **Database**: Included in Railway or separate ($10-20/month)
- **Total**: ~$30-100/month for moderate usage

---

## Troubleshooting

### "Cannot connect to backend"
- Check if backend is running
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings

### "Database connection error"
- Verify `DATABASE_URL` is correct
- Check if database is running
- Verify credentials

### "OpenAI API error"
- Check if API key is valid
- Verify you have credits
- Check rate limits

### "File upload fails"
- Check file size (max 10MB)
- Verify file format (PDF or TXT)
- Check upload directory permissions

---

## Security Checklist Before Launch

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set up rate limiting
- [ ] Add authentication (see AUTHENTICATION.md)
- [ ] Validate all inputs
- [ ] Set up monitoring

---

## Quick Reference

### URLs You'll Need
- **Backend API**: `https://your-app.railway.app`
- **Frontend**: `https://your-app.vercel.app`
- **API Docs**: `https://your-app.railway.app/docs`

### Environment Variables

**Backend (Railway)**:
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
SECRET_KEY=...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Frontend (Vercel)**:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Next Steps After Deployment

1. **Add Authentication** (see AUTHENTICATION.md)
2. **Test with real users**
3. **Set up monitoring** (Sentry, etc.)
4. **Configure backups**
5. **Set up custom domain** (optional)
6. **Launch!**

---

## Summary

✅ **Internet Required**: Yes, users need internet to access and use the app  
✅ **Easiest Deployment**: Railway (backend) + Vercel (frontend)  
✅ **Free Tier Available**: Yes, good for testing  
✅ **No Installation for Users**: It's a web app, works in browsers  
✅ **Works on Any Device**: Desktop, mobile, tablet - anything with internet  

The application is **cloud-based**, meaning it runs on servers on the internet. Users access it through their web browser, so they need an internet connection (WiFi, mobile data, or ethernet).



