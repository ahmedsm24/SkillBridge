# SkillBridge

An AI-powered application that analyzes resumes, identifies skill gaps compared to job requirements, and generates personalized training modules to bridge those gaps. This system is designed for research on "reverse human-machine learning" where humans learn from machine-generated training content.

## Overview

This application helps new hires quickly bridge skill gaps by:
1. **Parsing Resumes**: Extracts skills, experience, and education from resume documents (PDF/TXT)
2. **Analyzing Job Requirements**: Identifies required and preferred skills from job descriptions
3. **Gap Analysis**: Compares candidate skills with job requirements to identify gaps
4. **Training Module Generation**: Creates personalized training programs with modules, case studies, and practical exercises

## Architecture

The application consists of three main components:

### Backend (FastAPI)
- **Resume Parser**: Extracts information from PDF and text resumes
- **Gap Analyzer**: Compares skills and identifies gaps
- **Training Generator**: Creates personalized training modules
- **REST API**: Exposes endpoints for frontend interaction
- **Database**: SQLite/PostgreSQL for storing resumes, job descriptions, and training modules

### Frontend (Next.js)
- **Resume Upload**: File upload interface for resumes
- **Job Description Form**: Input form for job requirements
- **Gap Analysis Display**: Visualizes skill gaps and priorities
- **Training Module Viewer**: Interactive display of generated training content

### Agents (LangGraph)
- **Multi-Agent System**: Orchestrates specialized agents for analysis
- **Resume Analyzer Agent**: Extracts and structures resume data
- **Gap Analyzer Agent**: Identifies skill gaps
- **Training Generator Agent**: Creates training modules

## Features

- **Resume Parsing**: Supports PDF and text file formats
- **Skill Extraction**: Uses pattern matching and LLM-based extraction
- **Gap Analysis**: Identifies missing skills with priority ranking
- **Personalized Training**: Generates domain-specific training modules
- **Case Studies**: Includes relevant case studies for practical learning
- **Practical Exercises**: Hands-on exercises for skill development
- **Resource Recommendations**: Suggests papers, tutorials, and courses

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_api_key_here  # Optional but recommended
export DATABASE_URL=sqlite:///./resume_training.db

# Run the server
python -m uvicorn src.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variable (optional)
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Agents Setup

```bash
cd agents
pip install -r requirements.txt

# Run the agent system
python src/index.py
```

## Usage

### 1. Upload Resume
- Navigate to the application
- Upload a PDF or text resume
- The system extracts skills, experience, and education

### 2. Enter Job Description
- Provide job title, company, and full job description
- Specify the domain/industry (e.g., "biotech", "finance")
- The system extracts required and preferred skills

### 3. View Gap Analysis
- The system automatically compares resume skills with job requirements
- View existing skills (matches) and missing skills (gaps)
- See prioritized skill gaps with importance ratings

### 4. Generate Training Modules
- The system generates personalized training modules
- Each module includes:
  - Learning objectives
  - Content outline
  - Practical exercises
  - Estimated duration
  - Difficulty level
- View case studies and recommended resources

## API Endpoints

### Resumes
- `POST /api/v1/resumes/upload` - Upload and parse a resume
- `GET /api/v1/resumes/{id}` - Get resume by ID

### Job Descriptions
- `POST /api/v1/job-descriptions` - Create a job description
- `GET /api/v1/job-descriptions/{id}` - Get job description by ID

### Gap Analysis
- `POST /api/v1/gap-analysis` - Perform gap analysis
- `GET /api/v1/gap-analysis/{id}` - Get gap analysis results

### Training Modules
- `POST /api/v1/training-modules/generate` - Generate training modules
- `GET /api/v1/training-modules/{id}` - Get training module by ID
- `GET /api/v1/training-modules` - List all training modules

## Example Use Case

**Scenario**: A candidate with ML expertise applies for a Machine Learning Intern position at a biotech firm.

1. **Resume Analysis**: System extracts skills like "Python", "Machine Learning", "Deep Learning"
2. **Job Requirements**: Job requires "Causal Inference", "Health Data Analysis", "RCTs"
3. **Gap Identification**: System identifies missing skills:
   - Causal Inference (Critical, Priority 1)
   - Health Data Analysis (Critical, Priority 2)
   - RCTs (Important, Priority 3)
4. **Training Generation**: System creates modules:
   - Module 1: Causal Inference with Health Data
   - Module 2: Reading and Analyzing Health Data
   - Module 3: Randomized Controlled Trials (RCTs)
   - Includes biotech-specific case studies and exercises

## Configuration

### Environment Variables

**Backend**:
- `OPENAI_API_KEY`: OpenAI API key for LLM features (optional)
- `DATABASE_URL`: Database connection string (default: SQLite)

**Frontend**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

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

## Research Context

This application is designed for research on "reverse human-machine learning" - a paradigm where:
- Machines learn from humans (traditional ML)
- **Humans learn from machines** (this application)

The system acts as an AI trainer that:
- Analyzes what humans need to learn
- Generates personalized training content
- Provides case studies and practical exercises
- Replaces traditional human trainers for onboarding

## Future Enhancements

- Integration with learning management systems (LMS)
- Progress tracking and assessment
- Adaptive learning paths based on performance
- Multi-language support
- Integration with video content and interactive tutorials
- Collaborative learning features

## License

[Your License Here]

## Contributing

[Contributing Guidelines]



