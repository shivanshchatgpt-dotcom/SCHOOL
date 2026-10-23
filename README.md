# PySchool - Learn Python The School Way

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?logo=react&logoColor=white)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)

**PySchool** is a goal-oriented Python learning platform that mimics the structure of a real school. Instead of overwhelming learners with endless tutorials, PySchool asks *"What do you want to become?"*, assesses your current skill level, and delivers a structured 180-day curriculum tailored to your career goals.

![PySchool Homepage](docs/images/home.png)

## Features

### 🎯 Goal-Oriented Learning
- **Career-Focused Paths** - Choose from curated learning paths for Web Development, Data Science, AI/ML, Cybersecurity, and more
- **Intelligent Placement Testing** - 13-question assessments determine your starting point (Foundation, Beginner, Intermediate, or Advanced)
- **Personalized Learning Journey** - Automatically starts from the appropriate milestone based on your assessment results

### 📚 Structured Curriculum
- **180-Day Roadmap** - Complete, progressive curriculum spanning 6 months of structured learning
- **1-Hour Daily Classes** - Each lesson includes theory, worked examples, and practical exercises
- **Tiered Content** - Days 1-14 are hand-authored foundations, with expertly crafted content throughout
- **Domain-Specific Learning** - Advanced days focus on libraries and tools relevant to your chosen career path

### 💪 Interactive Practice & Assessment
- **Safe Code Evaluation** - Submissions are parsed with Python's AST module, never executed on the server
- **Smart Rubric Checking** - Validates syntax, required constructs, and coding patterns with whitespace-tolerant matching
- **Instant Feedback** - Get immediate results on your coding exercises
- **Milestone-Based Progression** - Pass rubric checks to advance, earn XP, and maintain streaks

### 📊 Progress Tracking
- **Gamified Learning** - Earn XP (+10/+15), build daily streaks, and track your progress
- **Dashboard Analytics** - Visualize your learning journey, completed days, and achievements
- **Resume Anytime** - Pick up exactly where you left off with persistent progress tracking

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[SQLite](https://www.sqlite.org/)** - Lightweight, serverless database
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python type hints
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server for production-grade performance

### Frontend
- **[React 18](https://reactjs.org/)** - Component-based UI library
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[Vite](https://vitejs.dev/)** - Next-generation frontend tooling
- **[React Router](https://reactrouter.com/)** - Client-side routing
- **[Tailwind CSS 4](https://tailwindcss.com/)** - Utility-first CSS framework

## Architecture

```
PySchool/
├── backend/           # FastAPI REST API
│   ├── app/
│   │   ├── routers/   # API endpoints (paths, assessment, lessons, etc.)
│   │   ├── models.py  # Data models
│   │   ├── db.py      # Database configuration
│   │   ├── seed.py    # Database seeding
│   │   └── curriculum_catalog.py # Curriculum generation logic
│   └── requirements.txt
├── frontend/          # React + TypeScript SPA
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/# Reusable UI components
│   │   └── api.ts     # API client
│   └── package.json
└── docs/             # Documentation and screenshots
```

## Getting Started

### Prerequisites
- **Python 3.9+** installed
- **Node.js 18+** and **npm** installed
- **Git** installed

### Installation & Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/shivanshchatgpt-dotcom/SCHOOL.git
cd SCHOOL
```

#### 2. Start the Backend API
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://127.0.0.1:8001`. The SQLite database is automatically created and seeded on first startup.

#### 3. Start the Frontend
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://127.0.0.1:5173`.

### Quick Reset (Development)
To reset the database and reseed with fresh data:
```bash
rm -f backend/pyschool.db
```
Restart the backend server to regenerate.

## Usage

1. **Choose Your Path** - Browse career paths and select one that aligns with your goals
2. **Take Placement Test** - Complete the assessment to determine your starting level
3. **Start Learning** - Follow your personalized daily lessons with theory and exercises
4. **Practice & Submit** - Write Python code and submit for automatic rubric validation
5. **Track Progress** - Monitor your XP, streaks, and advancement through the dashboard

![Learning Paths](docs/images/paths.png)

## Security

- **Safe Code Execution** - All user code is parsed via AST, never executed
- **Token-Based Authentication** - Student endpoints require enrollment tokens
- **Admin Protection** - Teacher/admin endpoints secured with `X-Admin-Token`
- **CORS Restrictions** - Configurable CORS origins for production deployment
- **Environment Configuration** - Sensitive values managed via environment variables

## Testing

Run the backend test suite:
```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with a focus on making Python education structured, goal-oriented, and accessible to learners of all levels.

---

**[Live Demo](http://127.0.0.1:5173)** | **[API Documentation](http://127.0.0.1:8001/docs)** | **[Report Issues](https://github.com/shivanshchatgpt-dotcom/SCHOOL/issues)**
