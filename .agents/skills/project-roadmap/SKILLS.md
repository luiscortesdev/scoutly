---
name: scoutly-project-roadmap
description: Provides complete architectural specifications, monorepo hierarchy, database schemas, and a 16-week execution timeline for Scoutly. Use this skill when planning features, scaffold-generating services, writing scrapers, designing API contracts, or deploying the system.
---

# Scoutly: System Specification

## 1. Project Mission & Core Features
The platform matches prospective high school golfers with NCAA/NAIA college golf programs based on athletic metrics, academic standing, and institutional preferences.

### Key Capabilities
*   **Athletic Fit Scoring:** Matches player scoring averages and tournament differentials against historical team rosters and tournament scorecards (evaluating starter vs. developmental/rotation roles).
*   **Academic Compatibility:** Cross-references player GPA, SAT/ACT, and intended majors with Department of Education (DOE) College Scorecard data.
*   **Institutional Filters:** Division (NCAA D1, D2, D3, NAIA), geographic region/state, tuition/budget (in-state vs. out-of-state), campus size, and public vs. private control.
*   **Comparative Insights:** Side-by-side program comparisons displaying golf performance metrics alongside academic stats and graduation outcomes.

---

## 2. Technical Stack & Architectural Decisions

| Layer | Technology | Deployment Target | Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js (App Router, TS), TailwindCSS, `shadcn/ui`, TanStack Query | Vercel (Hobby Tier) | Server-side rendering, zero-maintenance global CDN, accessible Radix-based UI components. |
| **Backend API** | Go (Chi/Gin) or Python (FastAPI) | AWS EC2 (Docker) | High-performance compiled service or async Python; strict separation of business logic from frontend. |
| **Database** | PostgreSQL 16 | AWS EC2 (Docker) | Relational integrity for normalized college, athletic, and user entities. |
| **ETL & Scraping** | Playwright (Python/Node.js) + Pandas | AWS EC2 (Cron) | Headless browser automation handling dynamic NCAA athletic sites and automated CSV ingestion. |
| **Reverse Proxy** | Nginx + Certbot (Let's Encrypt) | AWS EC2 (Docker) | Single entry point terminating TLS/SSL and forwarding to backend API. |
| **Cloud Hosting** | Single AWS EC2 (`t2.micro` or `t3.micro`) | AWS Free Tier | **Cost containment ($0):** Bypasses the ~$3.65/mo AWS public IPv4 RDS tax by co-locating Postgres inside Docker on EC2. |

---

## 3. Monorepo Directory Layout

Agents must maintain strict file boundaries according to the following layout:

```text
college-golf-matcher/
├── .gitignore                      # Monorepo root ignore (ignores node_modules, .env*, venv, etc.)
├── README.md                       # Architecture diagrams, local dev instructions
├── docker-compose.yml              # Local & staging orchestration (API + Postgres + Nginx)
│
├── frontend/                       # Next.js Application
│   ├── src/
│   │   ├── app/                    # Next.js App Router (layout, pages, routing)
│   │   ├── components/             # Reusable UI elements (shadcn/ui primitives)
│   │   ├── hooks/                  # Custom React hooks (TanStack queries/mutations)
│   │   ├── lib/                    # API client, utility functions
│   │   └── types/                  # Shared frontend TypeScript interfaces
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                        # Dedicated Backend Service
│   ├── Dockerfile
│   ├── cmd/api/                    # Application entry points (main.go / app.py)
│   ├── internal/                   # Private application logic (or app/ in FastAPI)
│   │   ├── handler/                # HTTP route handlers / controllers
│   │   ├── service/                # Matching engine & business logic
│   │   ├── repository/             # Database access queries & transactions
│   │   └── model/                  # Domain entity structs/models
│   ├── migrations/                 # Raw SQL or ORM schema migration files
│   └── go.mod (or pyproject.toml)
│
├── scraper/                        # Scrapers & Ingestion Pipelines
│   ├── Dockerfile
│   ├── scripts/                    # Entrypoints for scheduled scraping
│   │   ├── ncaa_roster_spider.py   # Playwright scrapers for rosters and scores
│   │   └── doe_scorecard_loader.py # Ingestion script for DOE CSV dataset
│   ├── parsers/                    # HTML/DOM extraction logic
│   └── requirements.txt
│
└── deploy/                         # Production Infrastructure Configuration
    └── nginx/
        └── conf.d/default.conf     # Nginx reverse proxy configuration and SSL routing
```

---

## 4. Database Schema Guidelines

Agents should model the PostgreSQL schema to maintain strict normalization:

1.  **`colleges`**: `id` (UUID/PK), `name`, `city`, `state`, `division`, `control` (public/private), `admission_rate`, `avg_sat`, `avg_act`, `avg_gpa`, `tuition_in_state`, `tuition_out_of_state`.
2.  **`golf_programs`**: `id` (PK), `college_id` (FK), `gender` (Men/Women), `head_coach`, `conference`, `national_scoring_rank`, `team_scoring_average`.
3.  **`roster_members`**: `id` (PK), `golf_program_id` (FK), `player_name`, `academic_year` (FR/SO/JR/SR), `individual_scoring_average`, `rounds_played`.
4.  **`users`**: `id` (PK), `email`, `password_hash` (Argon2id/Bcrypt), `created_at`.
5.  **`player_profiles`**: `id` (PK), `user_id` (FK), `gpa`, `sat_act_score`, `golf_scoring_average`, `target_division`, `budget_limit`.
6.  **`saved_matches`**: `id` (PK), `user_id` (FK), `college_id` (FK), `match_score`, `saved_at`.

---

## 5. Phased Development Roadmap

When assisting the developer, execute tasks aligned with these milestones:

### Phase 1: Data Engineering & Normalization (Weeks 1–3)
*   **Goal:** Build database schema and seed it with both DOE academic data and NCAA athletic data.
*   **Deliverables:**
    *   PostgreSQL schema defined with migrations.
    *   Automated script to ingest DOE College Scorecard CSV data.
    *   Playwright scraper collecting athletic rosters, scoring averages, and divisions.
    *   Normalization pipeline matching school name aliases (e.g., "UNC Chapel Hill" vs. "University of North Carolina at Chapel Hill").

### Phase 2: Core API & Matching Engine (Weeks 4–6)
*   **Goal:** Build and test the computational core in the backend API.
*   **Deliverables:**
    *   REST endpoints: `GET /api/v1/colleges`, `GET /api/v1/colleges/:id`.
    *   Implement `POST /api/v1/match` endpoint accepting golfer profiles.
    *   Matching Algorithm Logic: Compute weighted fitness scores based on:
        *   *Athletic Fitness (40%):* Difference between user scoring average and program average/roster cutoffs.
        *   *Academic Fitness (30%):* Alignment with middle 50% GPA/SAT/ACT percentiles.
        *   *Financial/Preference Alignment (30%):* Division, location, and tuition ceilings.

### Phase 3: Frontend Interface (Weeks 7–10)
*   **Goal:** Construct a responsive, modern Next.js interface using `shadcn/ui`.
*   **Deliverables:**
    *   Layouts generated via `v0.dev` / `shadcn/ui`: Search filters, college cards, score comparison views.
    *   State management with TanStack Query (fetching, caching, debounce filters).
    *   Side-by-side program comparison page.

### Phase 4: Authentication & User Profiles (Weeks 11–12)
*   **Goal:** Secure user state and implement saved search preferences.
*   **Deliverables:**
    *   User registration and login endpoints utilizing secure `HttpOnly` cookie-based JWT or session tokens.
    *   User dashboard storing golf handicap/differential and academic transcripts.
    *   Bookmark/save functionality for matched programs.

### Phase 5: Containerization & Cloud Deployment (Weeks 13–14)
*   **Goal:** Fully automate deployment to a single AWS EC2 instance at $0 cost.
*   **Deliverables:**
    *   Multi-stage `Dockerfile` definitions for backend API, scraper, and local PostgreSQL.
    *   `docker-compose.yml` tying services together within a private container network.
    *   Nginx reverse proxy forwarding traffic from port 80/443 to the backend API container.
    *   Frontend deployed to Vercel with environment variables pointing to the EC2 API endpoint.

### Phase 6: Production Hardening & Portfolio Assets (Weeks 15–16)
*   **Goal:** Ensure the project reflects FAANG/enterprise coding standards.
*   **Deliverables:**
    *   Root `README.md` containing architectural diagrams, system flow, and local reproduction instructions (`docker compose up --build`).
    *   Integration and unit tests for the matching engine algorithm.
    *   GitHub Actions CI pipeline running linting, formatting, and tests.

---

## 6. Implementation Guardrails for Agents

*   **Cloud Budget Constraint:** Never suggest or generate infrastructure that violates the $0 budget model. Do not configure standalone AWS RDS databases, Application Load Balancers (ALBs), or NAT Gateways. All state and backend logic run inside Docker on a single free-tier EC2 instance.
*   **Separation of Concerns:** Never put matching, scoring calculations, or raw database queries directly in the Next.js frontend code. The frontend must interact strictly via typed JSON HTTP endpoints exposed by the backend API.
*   **Component Architecture:** Use `shadcn/ui` components based on Radix UI primitives. Ensure all UI elements support keyboard accessibility and standard ARIA roles.
*   **Security Standards:** Ensure passwords are never stored in plaintext (enforce Argon2id or bcrypt). Validate all incoming inputs on the backend using data transfer objects (DTOs) or schemas (e.g., Pydantic or Go structs with validation tags).