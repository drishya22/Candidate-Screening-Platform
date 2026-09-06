# 🚀 AI-Powered Candidate Screening & Recruitment Automation Platform

> **An end-to-end AI recruitment platform that transforms candidate data, resumes, GitHub activity, and assessment performance into explainable candidate rankings and automated interview scheduling.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)](https://www.sqlalchemy.org/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Evaluation-4285F4.svg)](https://ai.google.dev/)
[![GitHub API](https://img.shields.io/badge/GitHub-Repository%20Analysis-181717.svg)](https://docs.github.com/en/rest)
[![Google Calendar](https://img.shields.io/badge/Google%20Calendar-Interview%20Automation-4285F4.svg)](https://developers.google.com/calendar/api)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

---

## 📌 Overview

Recruitment teams often spend significant time manually reviewing resumes, validating technical profiles, checking GitHub projects, comparing assessment scores, shortlisting candidates, and coordinating interviews.

This project provides a unified recruitment workflow that automates these steps through a modular backend and recruiter-facing dashboard.

The platform combines:

- Candidate dataset ingestion
- Resume downloading and PDF text extraction
- Job-description-aware AI evaluation
- Explainable candidate assessment
- Repository-level GitHub analysis
- Technical assessment result ingestion
- Weighted candidate ranking
- Automated interview scheduling
- Google Calendar integration
- Google Meet generation
- Recruiter dashboard and candidate comparison

The system is designed around a simple principle:

> **Automate repetitive recruitment operations while keeping the final evaluation traceable, evidence-driven, and understandable to a recruiter.**

---

# 🎯 Problem Statement

A typical technical hiring workflow involves several disconnected sources of information:

```text
Candidate Dataset
      │
      ├── Resume
      ├── Academic Information
      ├── Projects
      ├── Research
      ├── GitHub
      └── Assessment Results
```

Recruiters must manually combine these signals before making a decision.

This platform creates a unified screening pipeline:

```text
Candidate Data
      ↓
Resume Processing
      ↓
JD-Aware AI Evaluation
      ↓
Repository-Level GitHub Analysis
      ↓
Technical Test Analysis
      ↓
Weighted Ranking
      ↓
Shortlisting
      ↓
Automated Interview Scheduling
      ↓
Google Meet + Calendar Invitation
```

---

# ✨ Key Features

## 1. 📥 Dynamic Candidate Dataset Ingestion

Recruiters can upload candidate datasets rather than relying on hardcoded candidates.

Supported source formats include:

- CSV
- XLSX

Candidate information can include:

- Name
- Email
- College
- Branch
- CGPA
- Best AI Project
- Research Work
- GitHub Profile
- Resume Link

The ingestion layer normalizes column names, validates required fields, and prevents duplicate candidate creation.

---

## 2. 📄 Automated Resume Processing

The platform can process publicly accessible PDF resumes.

The resume pipeline:

```text
Resume URL
    ↓
URL Normalization
    ↓
PDF Download
    ↓
Content Validation
    ↓
SHA-256 Content Hash
    ↓
PDF Text Extraction
    ↓
Persist Extracted Resume
```

Google Drive-style resume URLs are normalized before downloading.

The extracted resume is then used as evidence for AI-based candidate evaluation.

### Why hashing?

A content hash provides a lightweight mechanism for detecting whether the underlying resume content has changed and creates a foundation for future incremental processing.

---

# 🧠 AI-Powered Candidate Evaluation

The AI evaluation layer uses a structured Gemini response rather than treating an LLM response as an unstructured paragraph.

Candidates are evaluated against the supplied Job Description using resume evidence.

### Evaluation dimensions

| Dimension | Weight |
|---|---:|
| Skills | 35% |
| Experience | 20% |
| Projects | 30% |
| Education | 15% |

The resulting AI score is calculated from these structured components.

### Evidence-first evaluation

The evaluation prompt explicitly instructs the model to:

- Use only evidence present in the resume
- Avoid inventing skills or experience
- Avoid giving credit for requirements that are not evidenced
- Prefer concrete projects and experience over isolated keywords
- Identify candidate strengths
- Identify candidate gaps
- Provide requirement-level evidence

This makes the output more useful to a recruiter than a generic LLM-generated candidate summary.

---

# 🔍 Explainable AI

The platform does not reduce the candidate to a single unexplained number.

The evaluation stores structured information such as:

```text
Skills Score
Experience Score
Project Score
Education Score

Strengths
Gaps
Requirement Evidence
Recommendation
```

This allows a recruiter to understand **why** a candidate received a particular evaluation.

---

# 🐙 Repository-Level GitHub Analysis

GitHub analysis is performed at the repository level rather than simply checking whether a candidate has a GitHub profile.

For each analyzed repository, the platform retrieves signals such as:

- Repository name
- Description
- Primary languages
- Stars
- Forks
- Commit count
- README content
- Repository URL

The system analyzes multiple public repositories from a candidate's profile.

---

## 📊 GitHub Scoring Methodology

The GitHub score is composed of several deterministic signals:

| Signal | Weight |
|---|---:|
| Repository relevance | 40% |
| Engineering signals | 25% |
| Activity | 20% |
| Documentation | 15% |

### Repository relevance

Repositories are evaluated for relevance to technical/AI-oriented work using repository metadata and content signals.

### Engineering signals

The system considers signals such as the proportion of repositories containing meaningful code/language information.

### Activity

Commit activity contributes to the score.

### Documentation

README availability and documentation quality contribute to the overall score.

This produces a reproducible GitHub score instead of an opaque LLM-only judgment.

---

# 🧪 Technical Test Integration

Assessment results can be uploaded independently of the candidate dataset.

Supported assessment fields include:

- Logical Aptitude Score
- Coding Test Score

The system matches test results to candidates using candidate identity fields.

Where email values differ between source datasets, the matching layer can fall back to:

```text
Candidate Name + College
```

This makes the ingestion pipeline more robust to inconsistencies between independently generated datasets.

---

# 🏆 Candidate Ranking

The final ranking combines three major sources of evidence:

```text
             ┌──────────────────┐
             │  AI Evaluation   │
             └────────┬─────────┘
                      │ 50%
                      ▼
             ┌──────────────────┐
             │ GitHub Analysis  │
             └────────┬─────────┘
                      │ 20%
                      ▼
             ┌──────────────────┐
             │ Test Performance │
             └────────┬─────────┘
                      │ 30%
                      ▼
               Final Candidate
                    Score
```

### Final Score

```text
AI Score       × 0.50
GitHub Score   × 0.20
Test Score     × 0.30
--------------------------------
Final Score
```

### AI Score

```text
Skills       × 0.35
Experience   × 0.20
Projects     × 0.30
Education    × 0.15
```

### Test Score

```text
Logical Aptitude × 0.40
Coding Test      × 0.60
```

The final system produces:

- Rank
- AI score
- GitHub score
- Test score
- Final score
- Recommendation

This gives recruiters both an overall ranking and the underlying signals that produced it.

---

# 📅 Automated Interview Scheduling

Shortlisted candidates can be scheduled through Google Calendar.

The scheduling flow is:

```text
Selected Candidate
       ↓
Interview Date / Time
       ↓
Google Calendar API
       ↓
Calendar Event
       ↓
Google Meet Conference
       ↓
Candidate Invitation
```

The platform uses Google's Calendar API to create an actual calendar event and request a Google Meet conference.

Candidate attendees can receive calendar invitations automatically.

---

# 🔐 Google OAuth Integration

Google Calendar access is authorized using OAuth.

The application requests calendar-event permissions and stores the resulting authorization token outside the source repository.

Sensitive credentials are deliberately excluded from version control.

Expected local credential files include:

```text
credentials/
token.json
```

These are ignored through `.gitignore`.

---

# 🖥️ Recruiter Dashboard

The frontend provides a recruiter-oriented view of the screening pipeline.

The dashboard is designed around quick decision making.

It provides:

- Candidate statistics
- Ranked candidate list
- AI score visualization
- GitHub score visualization
- Test score visualization
- Final ranking
- Recommendation status
- Candidate details
- Interview scheduling controls

The dashboard communicates with the FastAPI backend through REST endpoints.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │   Recruiter Dashboard │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
     ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
     │ Candidate Data │    │ Job / JD       │    │ Test Results   │
     │ Ingestion      │    │ Management     │    │ Ingestion      │
     └───────┬────────┘    └───────┬────────┘    └───────┬────────┘
             │                     │                     │
             ▼                     ▼                     │
     ┌────────────────┐    ┌────────────────┐            │
     │ Resume Service │    │ Gemini AI      │            │
     │ PDF Extraction │───►│ Evaluation     │            │
     └────────────────┘    └───────┬────────┘            │
                                   │                     │
                                   ▼                     │
                          ┌──────────────────┐            │
                          │ Evaluation Store │            │
                          └────────┬─────────┘            │
                                   │                     │
                    ┌──────────────┴──────────────┐      │
                    ▼                             ▼      ▼
           ┌────────────────┐            ┌────────────────┐
           │ GitHub Service │            │ Ranking Engine │
           │ Repository     │───────────►│               │
           │ Analysis       │            └───────┬────────┘
           └────────────────┘                    │
                                                ▼
                                      ┌────────────────────┐
                                      │ Candidate Ranking  │
                                      └─────────┬──────────┘
                                                │
                                                ▼
                                      ┌────────────────────┐
                                      │ Google Calendar    │
                                      │ + Google Meet      │
                                      └────────────────────┘
```

---

# 🔄 End-to-End Workflow

## Step 1 — Upload Candidates

The recruiter uploads a candidate dataset.

```text
CSV / XLSX
   ↓
Validation
   ↓
Normalization
   ↓
Duplicate Check
   ↓
Database
```

---

## Step 2 — Create Job Description

The recruiter provides:

- Job title
- Job description

The JD becomes the evaluation context for AI screening.

---

## Step 3 — Process Resumes

The platform downloads candidate resumes and extracts PDF text.

```text
Resume URL → PDF → Text → Database
```

---

## Step 4 — Evaluate Candidates

The AI service evaluates extracted resume evidence against the job description.

The evaluation is executed asynchronously so the HTTP request does not need to remain open while the full candidate batch is processed.

---

## Step 5 — Analyze GitHub

The GitHub service analyzes candidate repositories and stores structured repository-level information.

---

## Step 6 — Upload Test Results

Recruiters upload technical assessment results.

The ingestion layer associates those results with existing candidates.

---

## Step 7 — Rank Candidates

The ranking service combines:

```text
AI Evaluation
+
GitHub Analysis
+
Assessment Performance
```

and produces an ordered candidate list.

---

## Step 8 — Schedule Interviews

For selected candidates, the recruiter provides an interview time.

The platform creates:

- Google Calendar event
- Google Meet link
- Candidate invitation

---

# ⚡ Performance & Efficiency

The system is intentionally structured so expensive operations can be isolated from simple CRUD operations.

### Current efficiency considerations

- Duplicate candidate detection during ingestion
- Resume content hashing
- Structured AI outputs
- Concise AI prompts
- Background execution for batch AI evaluation
- Repository analysis limited to a manageable number of repositories
- Persistent structured evaluation records
- Deterministic scoring after AI processing
- Separation of ingestion, evaluation, GitHub analysis, ranking, and scheduling services

The architecture also makes it possible to introduce stronger caching and job queues without rewriting the entire application.

---

# 🧱 Technology Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Language | Python 3.11+ |
| ORM | SQLAlchemy |
| Database | SQLite for current deployment configuration |
| AI | Google Gemini |
| Resume Processing | pypdf |
| HTTP Client | httpx |
| GitHub Integration | PyGithub |
| Calendar | Google Calendar API |
| Meetings | Google Meet via Calendar API |
| Frontend | HTML / CSS / JavaScript |
| Containerization | Docker |
| Deployment | Render-compatible container / Python deployment |

---

# 📁 Project Structure

```text
Candidate-Screening-Platform/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── calendar.py
│   │       ├── candidates.py
│   │       ├── jobs.py
│   │       ├── screening.py
│   │       └── test_result.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── models/
│   │   ├── candidate.py
│   │   ├── database.py
│   │   ├── evaluation.py
│   │   ├── github_analysis.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   └── test_result.py
│   │
│   ├── schemas/
│   │   ├── candidate.py
│   │   ├── evaluation.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   └── test_result.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── calendar_service.py
│   │   ├── evaluation_service.py
│   │   ├── github_analysis_service.py
│   │   ├── github_service.py
│   │   ├── ranking_service.py
│   │   ├── resume_service.py
│   │   └── test_result_service.py
│   │
│   └── main.py
│
├── frontend/
│   └── index.html
│
├── credentials/
│   └── # local Google OAuth credentials (not committed)
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🔌 API Endpoints

## Candidate Management

### Upload candidates

```http
POST /api/candidates/upload
```

Accepts candidate dataset files.

---

## Job Management

### Create job

```http
POST /api/jobs/
```

Creates a job and stores its description.

### Process resumes

```http
POST /api/jobs/{job_id}/process-resumes
```

Downloads and extracts candidate resumes.

### Start AI evaluation

```http
POST /api/jobs/{job_id}/evaluate
```

Queues candidate evaluations for background processing.

---

## Test Results

### Upload test results

```http
POST /api/test-results/upload
```

Imports logical aptitude and coding assessment results.

---

## GitHub Analysis

### Analyze GitHub profiles

```http
POST /api/screening/github
```

Analyzes candidate GitHub repositories and stores GitHub scoring data.

---

## Ranking

### Retrieve rankings

```http
GET /api/screening/ranking/{job_id}
```

Returns candidate rankings with component scores and recommendations.

---

## Google Calendar

### Start OAuth

```http
GET /api/calendar/oauth/start
```

Starts Google Calendar authorization.

### OAuth callback

```http
GET /api/calendar/oauth/callback
```

Handles Google's authorization callback.

### Schedule interview

```http
POST /api/calendar/schedule
```

Creates a calendar event and Google Meet conference.

---

# ⚙️ Environment Configuration

Create a `.env` file for local development.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash

GITHUB_TOKEN=your_github_token

GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth/callback
GOOGLE_TOKEN_FILE=token.json
GOOGLE_CLIENT_SECRETS_FILE=credentials/google_client_secret.json

CALENDAR_TIMEZONE=Asia/Kolkata
```

### Important

Never commit:

```text
.env
.env.*
credentials/
token.json
```

API keys, OAuth client secrets, access tokens, and other credentials must remain outside source control.

---

# 🚀 Local Development

## 1. Clone the repository

```bash
git clone <repository-url>
cd Candidate-Screening-Platform
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create `.env` and configure the required credentials.

---

## 5. Configure Google Calendar

Create a Google OAuth client and place the downloaded client secret JSON at:

```text
credentials/google_client_secret.json
```

Make sure the configured OAuth redirect URI matches the environment configuration.

---

## 6. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

---

# 🐳 Docker

The application includes a Dockerfile for containerized execution.

Build the image:

```bash
docker build -t candidate-screening-platform .
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env candidate-screening-platform
```

The application listens on:

```text
0.0.0.0:8000
```

or the deployment platform's `$PORT` when provided.

---

# ☁️ Deployment

The application is designed to be compatible with cloud platforms that support Python web services or Docker containers.

A typical deployment configuration is:

### Build command

```bash
pip install -r requirements.txt
```

### Start command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables should be configured through the deployment platform's secret/environment-variable manager.

---

# 📈 Production Scalability

The current implementation is intentionally optimized for a time-constrained deployment while keeping service boundaries clear.

A production-scale version can evolve into:

```text
                    ┌───────────────┐
                    │ Load Balancer │
                    └───────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
          ┌──────▼──────┐       ┌──────▼──────┐
          │ API Worker  │       │ API Worker  │
          └──────┬──────┘       └──────┬──────┘
                 │                     │
                 └──────────┬──────────┘
                            │
                    ┌───────▼───────┐
                    │ PostgreSQL    │
                    └───────────────┘
                            │
                    ┌───────▼───────┐
                    │ Job Queue     │
                    │ Redis/Celery  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        Resume Worker   AI Worker   GitHub Worker
```

Potential production improvements include:

- PostgreSQL instead of local SQLite
- Redis-backed caching
- Celery/RQ/background workers
- Object storage for resume files
- Rate-limit aware external API clients
- Retry policies with exponential backoff
- Per-provider quotas
- Job status tracking
- Observability and structured logging
- Authentication and recruiter roles
- Database migrations with Alembic
- Horizontal API scaling

---

# 🛡️ Security Considerations

The platform handles candidate information and third-party credentials, so security is a first-class concern.

### Secrets

Credentials are provided through environment variables or ignored local files.

### GitHub

GitHub access uses a personal access token with restricted permissions.

### Google

Google Calendar uses OAuth rather than storing a user's Google password.

### Candidate data

Candidate datasets and local database files should not be committed to the public repository.

### AI evaluation

The AI prompt explicitly avoids using identity information as evaluation evidence.

---

# 🧪 Testing & Validation

The system has been validated across the major processing components during development.

Examples include:

- Candidate dataset ingestion
- Duplicate candidate handling
- Test-result ingestion
- Resume download
- PDF text extraction
- AI evaluation
- Background evaluation execution
- GitHub repository analysis
- GitHub profile analysis
- Candidate ranking
- Google Calendar integration flow

The architecture keeps deterministic scoring logic separate from AI generation so ranking calculations can be inspected independently of the LLM.

---

# ⚠️ Known Limitations

The current version was built as a practical recruitment automation prototype and has several areas that would require further hardening before production use.

### Database persistence

The current deployment configuration uses SQLite. A production deployment should use a managed PostgreSQL database.

### External API quotas

Gemini and GitHub APIs are subject to provider rate limits and quotas.

The architecture therefore separates AI evaluation and external integrations from deterministic ranking logic.

### Resume accessibility

Resume processing depends on the supplied URL being publicly accessible and returning a valid PDF.

### OAuth deployment

Google OAuth redirect URIs must be configured for the exact deployed application URL.

### Email provider

Recruitment email delivery should be connected to the recruiter's own email provider/service in a production implementation.

---

# 🔮 Future Improvements

## AI

- Multi-model evaluation
- Resume/JD embedding similarity
- Requirement-level semantic matching
- Evaluation confidence scores
- Human-in-the-loop review
- LLM-as-judge calibration
- Evaluation consistency checks

## GitHub

- Commit recency analysis
- Pull request analysis
- Issue participation
- Code-quality signals
- Repository activity timeline
- Deeper file-level analysis
- Repository architecture analysis

## Infrastructure

- PostgreSQL
- Redis caching
- Background workers
- Object storage
- Queue-based processing
- Retry and circuit-breaker mechanisms
- Distributed tracing

## Recruiter Experience

- Authentication
- Multiple jobs
- Pipeline stages
- Candidate search and filtering
- Manual override
- Recruiter notes
- Candidate comparison
- Bulk actions
- Email templates
- Analytics

## Ranking

Future versions could support configurable recruiter-defined weights rather than fixed scoring weights.

For example:

```text
AI Evaluation       50%
GitHub              20%
Technical Test      30%
```

could become configurable per job.

---

# 📋 Assignment Requirements Coverage

The platform was designed around the requested recruitment workflow.

| Requirement | Status |
|---|:---:|
| Candidate dataset upload | ✅ |
| Dynamic CSV/XLSX ingestion | ✅ |
| Resume download | ✅ |
| Resume text extraction | ✅ |
| Job description input | ✅ |
| AI candidate evaluation | ✅ |
| Evidence-based scoring | ✅ |
| Explainable evaluation | ✅ |
| Repository-level GitHub analysis | ✅ |
| Candidate scoring and ranking | ✅ |
| Technical test result upload | ✅ |
| Automated interview scheduling | ✅ |
| Google Calendar integration | ✅ |
| Google Meet generation | ✅ |
| Recruiter dashboard | ✅ |
| Docker support | ✅ |
| Public deployment support | 🚀 |
| Production-scale architecture path | ✅ |

---

# 🎬 Demo

A complete walkthrough demonstrates:

1. Candidate dataset ingestion
2. Job description creation
3. Resume processing
4. AI evaluation
5. GitHub analysis
6. Test-result integration
7. Candidate ranking
8. Recruiter dashboard
9. Interview scheduling
10. Google Calendar / Meet integration

**Demo video:** _Add deployed demo video link here._

---

# 💡 Design Philosophy

The platform intentionally separates three kinds of logic:

### 1. Probabilistic intelligence

Handled by Gemini for:

- Resume understanding
- JD-aware evaluation
- Strengths and gaps
- Requirement-level evidence

### 2. External factual signals

Handled by integrations for:

- GitHub repository activity
- Assessment scores
- Calendar availability and events

### 3. Deterministic business logic

Handled by application code for:

- Weighted scoring
- Ranking
- Duplicate detection
- Data validation
- Pipeline orchestration

This separation improves transparency and makes the system easier to debug, test, optimize, and evolve.

---

# 🧩 Why This Architecture?

Rather than building one large AI agent responsible for the entire recruitment workflow, the system uses specialized services.

```text
AI Service
    │
    ├── Understands candidate evidence
    │
GitHub Service
    │
    ├── Retrieves repository signals
    │
Resume Service
    │
    ├── Downloads and extracts resumes
    │
Test Result Service
    │
    ├── Normalizes assessment data
    │
Ranking Service
    │
    ├── Applies deterministic business rules
    │
Calendar Service
    │
    └── Automates interviews
```

This approach makes individual components replaceable without redesigning the entire application.

---

# 🌟 Project Highlights

### Evidence-driven AI

The LLM is constrained to evidence found in the candidate's resume rather than being encouraged to infer missing qualifications.

### Hybrid scoring

The final ranking combines AI-generated assessment with deterministic external signals.

### Repository-level GitHub analysis

GitHub evaluation goes beyond profile existence and analyzes actual repositories.

### Automation

The system covers the recruitment journey from candidate ingestion through interview scheduling.

### Deployment-aware design

External credentials are separated from source code, Docker support is included, and the architecture has a clear migration path toward PostgreSQL, caching, workers, and horizontal scaling.

---

# 📄 License

This project was created as part of a technical assignment / recruitment evaluation.

Add an appropriate license before open-source distribution if required.

---

# 👩‍💻 Author

**Drishya Garg**

AI / Backend Engineering • Python • FastAPI • LLM Applications • AI Systems

---

<p align="center">
  <strong>Built to turn candidate screening from a collection of manual tasks into one automated, explainable workflow.</strong>
</p>
