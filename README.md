# CodeTwin

**AI Digital Twin for Codebases with Predictive Refactoring**

CodeTwin is a sophisticated developer tool that creates a dynamic, multi-dimensional model (Digital Twin) of any software repository. It analyzes architecture, predicts risks, and provides actionable refactoring recommendations.

## 🚀 Key Features

- **Codebase Digital Twin**: A graph-based semantic model of your code.
- **Predictive Risk Analysis**: Identify high-complexity hotspots and critical dependency paths.
- **AI-Powered Refactoring**: Receive context-aware suggestions for modularization and technical debt reduction.
- **Impact Simulation**: Visualize the "Blast Radius" of potential changes before implementing them.
- **Interactive Architecture Map**: Explore your system's design using interactive force-directed graphs.

## 🏗️ Architecture

- **Frontend**: Next.js, TypeScript, D3.js, TailwindCSS.
- **Backend**: FastAPI (Python), PostgreSQL, Redis.
- **Analysis Engine**: Tree-sitter, NetworkX, Radon.
- **AI Layer**: SentenceTransformers, Vector Embeddings.

## 📂 Project Structure

- `frontend/`: Web interface for repository health monitoring and visualization.
- `backend/`: API layer for orchestration and data persistence.
- `analysis_engine/`: Core logic for parsing AST and building dependency graphs.
- `ai_service/`: AI embedding service for semantic code understanding.
- `docker/`: Deployment configurations.

## 🛠️ Getting Started

Follow these steps to set up CodeTwin for local development and exploration.

### 1. Prerequisites
- **Node.js 18+** & **npm**
- **Python 3.10+**
- **Redis Server** (required for the analysis worker queue)

### 2. Backend Setup
1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   > [!IMPORTANT]
   > Ensure you have C++ build tools installed for `tree-sitter` compilation.
   ```bash
   pip install -r requirements.txt
   ```
4. **Database Initialization**:
   By default, the system uses a **SQLite** database (`backend/sql_app.db`) for a fast, zero-config setup. To initialize and seed the demo data:
   ```bash
   # In the backend directory
   python seed_db.py
   ```

### 3. Frontend Setup
1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```

### 4. Running the Application
To run the full stack, you'll need three terminal sessions:

**Session 1: Backend API**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Session 2: Analysis Worker**
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

**Session 3: Frontend**
```bash
cd frontend
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

---

### 💡 Note on Intelligence Features
If `tree-sitter` or `psycopg2` fail to install due to environment constraints, the backend will still start in **"Demo Mode"** and serve architectural mock data for exploration.

---
Designed by **CodeTwin Development Team**
