# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key for enhanced features
export OPENAI_API_KEY=your_api_key_here

# Start the backend server
python -m uvicorn src.main:app --reload
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Using the Application

1. **Upload Resume**: 
   - Go to `http://localhost:3000`
   - Click "Upload Resume" and select a PDF or text file
   - Wait for the system to extract skills

2. **Enter Job Description**:
   - Fill in the job title, company (optional), and domain
   - Paste the full job description
   - Click "Create Job Description"

3. **View Gap Analysis**:
   - The system automatically performs gap analysis
   - View existing skills (green) and missing skills (red)
   - Review prioritized skill gaps

4. **Generate Training Modules**:
   - Click "Generate Training Modules"
   - Browse through the generated modules
   - Each module includes:
     - Learning objectives
     - Content outline
     - Practical exercises
     - Case studies
     - Recommended resources

## Example Workflow

**Scenario**: ML candidate applying for Biotech ML Intern position

1. Upload resume with skills: Python, Machine Learning, Deep Learning
2. Enter job description requiring: Causal Inference, Health Data Analysis, RCTs
3. System identifies gaps: Causal Inference (critical), Health Data (critical), RCTs (important)
4. System generates training modules:
   - Module 1: Causal Inference with Health Data (2 weeks)
   - Module 2: Health Data Analysis (2 weeks)
   - Module 3: Randomized Controlled Trials (1 week)
   - Includes biotech case studies and practical exercises

## Troubleshooting

### Backend Issues

- **Port already in use**: Change the port in `uvicorn` command: `--port 8001`
- **Database errors**: Delete `resume_training.db` and restart the server
- **Import errors**: Ensure you're in the backend directory and dependencies are installed

### Frontend Issues

- **API connection errors**: Check that backend is running on port 8000
- **Build errors**: Delete `node_modules` and `.next` folder, then run `npm install` again
- **Port conflicts**: Change port: `npm run dev -- -p 3001`

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
cd backend
black .
flake8 .

# Frontend
cd frontend
npm run lint
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./resume_training.db
```

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

- Review the generated training modules
- Customize the training content as needed
- Track progress through the modules
- Use the case studies for practical learning



