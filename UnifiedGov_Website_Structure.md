# UnifiedGov — Complete Website Structure

An information + official-link aggregator for Indian government exams. Users discover, filter, and read exam details on UnifiedGov, then click through to the official government site to actually apply.

---

## 1. Site Map / Pages

```
/
├── Home                          (hero search + featured/urgent exams + "browse by" tiles)
├── /state                        (list of all states — grid or map)
│   └── /state/[state-slug]       (e.g. /state/andhra-pradesh — exams for that state)
├── /central                      (list of central orgs — UPSC, SSC, IBPS, SBI, RRB, DRDO, ISRO, Army, Navy, Air Force...)
│   └── /central/[org-slug]       (e.g. /central/ssc — exams for that organization)
├── /category                     (browse by post type — Banking, Railways, Defence, Teaching, Police, PSC, Clerical...)
│   └── /category/[category-slug]
├── /exam/[exam-slug]             (single exam detail page — the core content unit)
├── /search                       (search + combined filters: state, category, org, status, qualification)
├── /latest                       (newly added / recently updated notifications)
├── /results                      (exam results & answer keys, optional phase 2)
├── /about
├── /disclaimer                   (critical — see Section 5)
├── /contact
└── /admin/*                      (protected — see Section 4)
```

**Navigation bar:** Home · State Exams · Central Exams · Categories · Latest · Search
**Footer:** About · Disclaimer · Contact · "Not affiliated with any government body" notice

---

## 2. Exam Categories (Taxonomy)

### A. By Geography
- **State** — Andhra Pradesh, Telangana, Karnataka, Tamil Nadu, Maharashtra, ... (all 28 states + 8 UTs)
- **Central** — All-India recruitment, not tied to one state

### B. By Organization (examples to seed the database)
| Scope | Organizations |
|---|---|
| Central | UPSC, SSC, IBPS, SBI, RBI, Railway (RRB/RRC), DRDO, ISRO, Indian Army, Indian Navy, Indian Air Force, CRPF/BSF/CISF (Paramilitary) |
| State (per state) | State PSC, State Police Recruitment Board, State Teacher Eligibility Board, State Cooperative Bank, State Electricity Board |

### C. By Post / Category
Banking · SSC (Clerical/Group B/C) · Railways · Defence · Teaching · Police · Administration (PSC) · Judicial · Engineering · Medical/Paramedical

A single exam can belong to **one state (or Central)** + **one organization** + **one or more categories** — this is what makes filtering powerful.

---

## 3. Exam Detail Page — Fields

Each exam/post page shows a standard fact-sheet, e.g. for **SSC CGL 2026**:

| Field | Example |
|---|---|
| Organization | Staff Selection Commission |
| Post | Group B / C |
| Scope | Central |
| Category | Clerical |
| Qualification | Graduation |
| Age Limit | 18–32 (as per notification) |
| Application Start Date | — |
| Last Date to Apply | — |
| Exam Date | — |
| Application Fee | — |
| Status | 🟢 Open / 🟡 Closing Soon / 🔴 Closed / ⚪ Upcoming |
| Official Notification | [PDF link] |
| Apply Online | [Official portal link — opens in new tab] |
| Last Verified | auto-stamped date |

**Apply Online always redirects off-site** to the official recruitment page. UnifiedGov never hosts an application form, collects personal data for applications, or accepts payments.

---

## 4. Database Schema (relational — matches the FastAPI + SQL stack)

```sql
-- Geography
states (
  id INT PK,
  name VARCHAR,
  slug VARCHAR UNIQUE
)

-- Issuing organizations (state or central)
organizations (
  id INT PK,
  name VARCHAR,              -- "Staff Selection Commission"
  slug VARCHAR UNIQUE,
  scope ENUM('state','central'),
  state_id INT NULL FK -> states.id,   -- NULL if central
  logo_url VARCHAR NULL,
  official_website VARCHAR
)

-- Post/category taxonomy (many-to-many with exams)
categories (
  id INT PK,
  name VARCHAR,               -- "Banking", "Railways", "Police"
  slug VARCHAR UNIQUE
)

-- Core exam/post listing
exams (
  id INT PK,
  title VARCHAR,               -- "SSC CGL 2026"
  slug VARCHAR UNIQUE,
  organization_id INT FK -> organizations.id,
  state_id INT NULL FK -> states.id,   -- NULL if central-only
  qualification VARCHAR,
  age_limit VARCHAR,
  application_start_date DATE NULL,
  application_end_date DATE NULL,
  exam_date DATE NULL,
  application_fee VARCHAR,
  status ENUM('upcoming','open','closing_soon','closed'),
  vacancies INT NULL,
  short_description TEXT,
  notification_pdf_url VARCHAR,
  apply_online_url VARCHAR,        -- external, official
  official_source_url VARCHAR,     -- where the data was verified from
  is_verified BOOLEAN DEFAULT FALSE,
  last_verified_at DATETIME,
  created_at DATETIME,
  updated_at DATETIME
)

-- Many-to-many: exam <-> category
exam_categories (
  exam_id INT FK -> exams.id,
  category_id INT FK -> categories.id,
  PRIMARY KEY (exam_id, category_id)
)

-- Admin/editor accounts (internal only — not applicant accounts)
admin_users (
  id INT PK,
  name VARCHAR,
  email VARCHAR UNIQUE,
  password_hash VARCHAR,
  role ENUM('editor','admin'),
  created_at DATETIME
)

-- Audit trail for every content change
exam_audit_log (
  id INT PK,
  exam_id INT FK -> exams.id,
  admin_user_id INT FK -> admin_users.id,
  action VARCHAR,             -- "created" / "updated" / "status_changed"
  field_changed VARCHAR NULL,
  old_value TEXT NULL,
  new_value TEXT NULL,
  changed_at DATETIME
)

-- Optional (phase 2): user accounts for saving/tracking, no application data
users (
  id INT PK,
  email VARCHAR UNIQUE,
  name VARCHAR,
  created_at DATETIME
)

saved_exams (
  user_id INT FK -> users.id,
  exam_id INT FK -> exams.id,
  saved_at DATETIME,
  PRIMARY KEY (user_id, exam_id)
)
```

**Indexes worth adding:** `exams(status)`, `exams(state_id)`, `exams(organization_id)`, `exams(application_end_date)` — these back the home page "closing soon" widget and the state/category filters.

**Note on `users`/`saved_exams`:** this is only for bookmarking and deadline reminders inside UnifiedGov — it is explicitly **not** an application-submission table. No aadhaar/ID numbers, no payment info, no exam-application forms are ever stored.

---

## 5. Trust & Compliance Notes

- **Disclaimer page (required):** "UnifiedGov is an independent information portal. We are not affiliated with, endorsed by, or officially connected to any government body. All applications must be submitted on the respective official websites, linked from each listing."
- **Every "Apply Online" button** opens the *official* domain in a new tab — never a redirect through a UnifiedGov-hosted form.
- **Source attribution per listing** — `official_source_url` lets admins (and users) trace every fact back to the government notification it came from.
- **Verification workflow** — `is_verified` + `last_verified_at` flags stale listings so nothing goes live (or stays live) without a human checking it against the current official notification.

---

## 6. Admin Panel

**Pages:**
- Dashboard — counts (open/closing soon/closed), recently added, listings needing re-verification (>30 days since `last_verified_at`)
- Exams — table view with filters (state, org, category, status), create/edit/delete, bulk status update
- Organizations — CRUD for issuing bodies
- States & Categories — CRUD for taxonomy
- Audit Log — read-only history of who changed what
- Editors — admin can invite/manage editor accounts (role-based access: editors can create/edit but not delete or manage users)

**Exam edit form** mirrors the schema fields above, with:
- A required "Official Notification URL" before publishing
- A status dropdown that auto-suggests "closing_soon" when `application_end_date` is within 5 days
- A preview pane showing exactly how the public exam card/detail page will render

---

## 7. Frontend Pages — Component Notes (React / Streamlit for prototype)

- **Home:** search bar (autocomplete on exam title/org), "Closing Soon" carousel, State grid, Central org grid
- **State/Central/Category listing pages:** filter sidebar (status, category, qualification) + card grid, same `ExamCard` component reused everywhere
- **Exam detail page:** fact-sheet table + two buttons — "View Official Notification" (PDF) and "Apply Online" (external, opens new tab, `rel="noopener noreferrer"`)
- **Search page:** combined filter state synced to URL query params so results are shareable/bookmarkable

---

## 8. Suggested Build Order (matches your prototype scope)

1. `states`, `organizations`, `categories`, `exams`, `exam_categories` tables + seed data for 3–4 states + Central
2. FastAPI endpoints: `GET /exams`, `GET /exams/{slug}`, `GET /states`, `GET /organizations`, filter query params
3. React/Streamlit listing + detail pages consuming those endpoints
4. Minimal admin CRUD (even a simple form-based editor is enough for the prototype)
5. Add `is_verified` / `last_verified_at` + disclaimer page before showing this to real users
