# How to Run the Application

## Quick Start

### Terminal 1: Start Backend

```bash
cd /Users/ahmed/Desktop/larsonwork/backend
source venv/bin/activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

### Terminal 2: Start Frontend

```bash
cd /Users/ahmed/Desktop/larsonwork/frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Access the Application

1. Open your web browser
2. Go to: **http://localhost:3000**
3. Start using the application!

## Troubleshooting

### Backend Issues

**If dependencies are missing:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**If port 8000 is in use:**
```bash
# Use a different port
python -m uvicorn src.main:app --reload --port 8001
```

### Frontend Issues

**If npm install fails:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**If port 3000 is in use:**
```bash
# Use a different port
npm run dev -- -p 3001
```

## Environment Variables (Optional)

Create `.env` file in `backend/` directory:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./resume_training.db
```

## Testing

1. **Test Backend**: Visit http://localhost:8000/docs
2. **Test Frontend**: Visit http://localhost:3000
3. **Upload a resume**: Try uploading a PDF or text file
4. **Enter job description**: Fill in the form
5. **View results**: See gap analysis and training modules



