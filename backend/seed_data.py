"""
Seeds the database with all 28 states + 8 union territories + Central,
each state's Public Service Commission (or equivalent), a handful of
central organizations, categories, and 7 sample exams spanning every status.

NOTE: state PSC website URLs are sourced from public knowledge and should
be re-verified against each commission's current live domain before this
goes near real users (see README "Before This Goes Near Real Users" /
the is_verified + last_verified_at workflow in the design doc).

Run: python3 seed_data.py   (drops & recreates all tables first)
"""
from datetime import date, datetime, timedelta

from backend.database import Base, engine, SessionLocal
from backend.models import State, Organization, Category, Exam, ScopeEnum, StatusEnum

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ---------- States (all 28) + Union Territories (all 8) ----------
STATE_NAMES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
]
UT_NAMES = [
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


def slugify(name: str) -> str:
    return name.lower().replace(" and ", "-").replace(" ", "-")


states = {
    slugify(name): State(name=name, slug=slugify(name))
    for name in STATE_NAMES + UT_NAMES
}
db.add_all(states.values())
db.flush()

# ---------- Organizations ----------
# Central bodies + each state/UT's Public Service Commission or equivalent
# recruiting authority.
orgs = {
    "ssc": Organization(name="Staff Selection Commission", slug="ssc",
                         scope=ScopeEnum.central, official_website="https://ssc.gov.in"),
    "ibps": Organization(name="Institute of Banking Personnel Selection", slug="ibps",
                          scope=ScopeEnum.central, official_website="https://ibps.in"),
    "upsc": Organization(name="Union Public Service Commission", slug="upsc",
                          scope=ScopeEnum.central, official_website="https://upsc.gov.in"),
    "rrb": Organization(name="Railway Recruitment Board", slug="rrb",
                         scope=ScopeEnum.central, official_website="https://rrb.indianrailways.gov.in"),
    "ap-police": Organization(name="AP Police Recruitment Board", slug="ap-police",
                               scope=ScopeEnum.state, state_id=states["andhra-pradesh"].id,
                               official_website="https://slprb.ap.gov.in"),
}

# State/UT Public Service Commissions (one per state/UT with a dedicated
# commission; a few small UTs are served only by Central bodies and are
# intentionally omitted here).
STATE_PSCS = {
    "andhra-pradesh": ("Andhra Pradesh PSC", "https://psc.ap.gov.in"),
    "arunachal-pradesh": ("Arunachal Pradesh PSC", "https://appsc.gov.in"),
    "assam": ("Assam PSC", "https://apsc.nic.in"),
    "bihar": ("Bihar PSC", "https://bpsc.bihar.gov.in"),
    "chhattisgarh": ("Chhattisgarh PSC", "https://psc.cg.gov.in"),
    "goa": ("Goa PSC", "https://gpsc.goa.gov.in"),
    "gujarat": ("Gujarat PSC", "https://gpsc.gujarat.gov.in"),
    "haryana": ("Haryana PSC", "https://hpsc.gov.in"),
    "himachal-pradesh": ("Himachal Pradesh PSC", "https://hppsc.hp.gov.in"),
    "jharkhand": ("Jharkhand PSC", "https://jpsc.gov.in"),
    "karnataka": ("Karnataka PSC", "https://kpsc.kar.nic.in"),
    "kerala": ("Kerala PSC", "https://keralapsc.gov.in"),
    "madhya-pradesh": ("Madhya Pradesh PSC", "https://mppsc.mp.gov.in"),
    "maharashtra": ("Maharashtra PSC", "https://mpsc.gov.in"),
    "manipur": ("Manipur PSC", "https://mpscmanipur.gov.in"),
    "meghalaya": ("Meghalaya PSC", "https://mpsc.nic.in"),
    "mizoram": ("Mizoram PSC", "https://mpsc.mizoram.gov.in"),
    "nagaland": ("Nagaland PSC", "https://npsc.nagaland.gov.in"),
    "odisha": ("Odisha PSC", "https://opsc.gov.in"),
    "punjab": ("Punjab PSC", "https://ppsc.gov.in"),
    "rajasthan": ("Rajasthan PSC", "https://rpsc.rajasthan.gov.in"),
    "sikkim": ("Sikkim PSC", "https://spscskm.gov.in"),
    "tamil-nadu": ("Tamil Nadu PSC", "https://tnpsc.gov.in"),
    "telangana": ("Telangana State PSC", "https://tspsc.gov.in"),
    "tripura": ("Tripura PSC", "https://tpsc.tripura.gov.in"),
    "uttar-pradesh": ("Uttar Pradesh PSC", "https://uppsc.up.nic.in"),
    "uttarakhand": ("Uttarakhand PSC", "https://ukpsc.net"),
    "west-bengal": ("West Bengal PSC", "https://wbpsc.gov.in"),
    "delhi": ("Delhi Subordinate Services Selection Board", "https://dsssb.delhi.gov.in"),
    "jammu-kashmir": ("Jammu & Kashmir PSC", "https://jkpsc.nic.in"),
    "puducherry": ("Puducherry PSC", "https://psc.py.gov.in"),
}

for state_slug, (org_name, url) in STATE_PSCS.items():
    org_slug = f"{state_slug}-psc"
    orgs[org_slug] = Organization(
        name=org_name, slug=org_slug, scope=ScopeEnum.state,
        state_id=states[state_slug].id, official_website=url,
    )

db.add_all(orgs.values())
db.flush()

# ---------- Categories ----------
cat_names = ["Banking", "SSC", "Railways", "Defence", "Teaching",
             "Police", "Administration", "Judicial", "Engineering", "Medical"]
categories = {n: Category(name=n, slug=n.lower().replace(" ", "-")) for n in cat_names}
db.add_all(categories.values())
db.flush()

today = date.today()


def d(offset_days):
    return today + timedelta(days=offset_days)


# ---------- Exams (7 sample rows, every status represented) ----------
# Only a handful of states have a seeded sample exam so far — the rest of
# the 36 states/UTs are fully browsable (their PSC shows up under
# State-wise) but have no listings yet until real notifications are added.
exams = [
    Exam(
        title="SSC CGL 2026", slug="ssc-cgl-2026",
        organization_id=orgs["ssc"].id, state_id=None,
        qualification="Graduation", age_limit="18-32",
        application_start_date=d(-10), application_end_date=d(3),
        exam_date=d(60), application_fee="Rs. 100",
        status=StatusEnum.closing_soon, vacancies=12000,
        short_description="Combined Graduate Level exam for Group B/C posts.",
        notification_pdf_url="https://ssc.gov.in",
        apply_online_url="https://ssc.gov.in",
        official_source_url="https://ssc.gov.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["SSC"], categories["Administration"]],
    ),
    Exam(
        title="IBPS PO 2026", slug="ibps-po-2026",
        organization_id=orgs["ibps"].id, state_id=None,
        qualification="Graduation", age_limit="20-30",
        application_start_date=d(-30), application_end_date=d(15),
        exam_date=d(90), application_fee="Rs. 850",
        status=StatusEnum.open, vacancies=4500,
        short_description="Probationary Officer recruitment across public sector banks.",
        notification_pdf_url="https://ibps.in",
        apply_online_url="https://ibps.in",
        official_source_url="https://ibps.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Banking"]],
    ),
    Exam(
        title="UPSC Civil Services 2026", slug="upsc-cse-2026",
        organization_id=orgs["upsc"].id, state_id=None,
        qualification="Graduation", age_limit="21-32",
        application_start_date=d(20), application_end_date=d(50),
        exam_date=d(150), application_fee="Rs. 100",
        status=StatusEnum.upcoming, vacancies=1000,
        short_description="Civil Services Examination for IAS/IPS/IFS and allied services.",
        notification_pdf_url="https://upsc.gov.in",
        apply_online_url="https://upsc.gov.in",
        official_source_url="https://upsc.gov.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Administration"]],
    ),
    Exam(
        title="RRB NTPC 2026", slug="rrb-ntpc-2026",
        organization_id=orgs["rrb"].id, state_id=None,
        qualification="Graduation / 12th pass", age_limit="18-33",
        application_start_date=d(-60), application_end_date=d(-5),
        exam_date=d(-2), application_fee="Rs. 500",
        status=StatusEnum.closed, vacancies=8000,
        short_description="Non-Technical Popular Categories recruitment on Indian Railways.",
        notification_pdf_url="https://rrb.indianrailways.gov.in",
        apply_online_url="https://rrbapply.gov.in",
        official_source_url="https://rrb.indianrailways.gov.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Railways"]],
    ),
    Exam(
        title="AP Police SI 2026", slug="ap-police-si-2026",
        organization_id=orgs["ap-police"].id, state_id=states["andhra-pradesh"].id,
        qualification="Graduation", age_limit="21-25",
        application_start_date=d(-5), application_end_date=d(10),
        exam_date=d(70), application_fee="Rs. 300",
        status=StatusEnum.open, vacancies=600,
        short_description="Sub-Inspector recruitment for Andhra Pradesh Police.",
        notification_pdf_url="https://slprb.ap.gov.in",
        apply_online_url="https://slprb.ap.gov.in",
        official_source_url="https://slprb.ap.gov.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Police"]],
    ),
    Exam(
        title="TSPSC Group 2 2026", slug="tspsc-group-2-2026",
        organization_id=orgs["telangana-psc"].id, state_id=states["telangana"].id,
        qualification="Graduation", age_limit="18-44",
        application_start_date=d(-15), application_end_date=d(2),
        exam_date=d(45), application_fee="Rs. 200",
        status=StatusEnum.closing_soon, vacancies=780,
        short_description="Group 2 services recruitment for Telangana state government.",
        notification_pdf_url="https://tspsc.gov.in",
        apply_online_url="https://tspsc.gov.in",
        official_source_url="https://tspsc.gov.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Administration"]],
    ),
    Exam(
        title="KPSC Gazetted Probationers 2026", slug="kpsc-gp-2026",
        organization_id=orgs["karnataka-psc"].id, state_id=states["karnataka"].id,
        qualification="Graduation", age_limit="21-35",
        application_start_date=d(30), application_end_date=d(60),
        exam_date=d(120), application_fee="Rs. 250",
        status=StatusEnum.upcoming, vacancies=340,
        short_description="Gazetted Probationers recruitment for Karnataka state services.",
        notification_pdf_url="https://kpsc.kar.nic.in",
        apply_online_url="https://kpsconline.karnataka.gov.in",
        official_source_url="https://kpsc.kar.nic.in", is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories["Administration"]],
    ),
]

# ---------- More state exams (data-driven) ----------
# One combined-competitive-style exam per remaining state PSC, so every
# major state has at least one browsable listing (27+ exams total).
# rows: (state_slug, exam_title, slug_suffix, category_key, status,
#        start_offset, end_offset, exam_offset, fee, vacancies,
#        qualification, age_limit, description)
MORE_EXAMS = [
    ("bihar", "BPSC 71st Combined Competitive Exam 2026", "bpsc-71-cce-2026",
     "Administration", StatusEnum.open, -20, 12, 80, "Rs. 150", 1500,
     "Graduation", "20-40", "Combined Competitive Examination for Bihar state civil services."),
    ("uttar-pradesh", "UPPSC PCS 2026", "uppsc-pcs-2026",
     "Administration", StatusEnum.closing_soon, -25, 4, 90, "Rs. 125", 250,
     "Graduation", "21-40", "Provincial Civil Service exam for UP state administrative posts."),
    ("maharashtra", "MPSC State Services 2026", "mpsc-state-services-2026",
     "Administration", StatusEnum.upcoming, 10, 40, 110, "Rs. 373", 400,
     "Graduation", "19-38", "Combined State Services exam for Maharashtra government posts."),
    ("west-bengal", "WBPSC Miscellaneous Services 2026", "wbpsc-misc-2026",
     "Administration", StatusEnum.open, -18, 9, 75, "Rs. 210", 300,
     "Graduation", "20-39", "Combined recruitment for various West Bengal state department posts."),
    ("madhya-pradesh", "MPPSC State Service Exam 2026", "mppsc-state-service-2026",
     "Administration", StatusEnum.closing_soon, -22, 3, 85, "Rs. 500", 220,
     "Graduation", "21-40", "State Service Examination for MP administrative and allied posts."),
    ("rajasthan", "RPSC RAS 2026", "rpsc-ras-2026",
     "Administration", StatusEnum.open, -12, 18, 95, "Rs. 350", 733,
     "Graduation", "21-40", "Rajasthan Administrative Service combined competitive exam."),
    ("gujarat", "GPSC Class 1-2 Exam 2026", "gpsc-class-1-2-2026",
     "Administration", StatusEnum.upcoming, 15, 45, 120, "Rs. 100", 180,
     "Graduation", "21-40", "Combined recruitment for Gujarat Class 1 and Class 2 gazetted posts."),
    ("punjab", "PPSC Civil Services 2026", "ppsc-civil-services-2026",
     "Administration", StatusEnum.open, -8, 22, 100, "Rs. 250", 90,
     "Graduation", "21-37", "Punjab Civil Services combined competitive examination."),
    ("kerala", "Kerala PSC LD Clerk 2026", "kerala-psc-ld-clerk-2026",
     "Administration", StatusEnum.closing_soon, -20, 5, 60, "Rs. 20", 1200,
     "Plus Two / Graduation", "18-36", "Lower Division Clerk recruitment across Kerala government departments."),
    ("odisha", "OPSC OCS 2026", "opsc-ocs-2026",
     "Administration", StatusEnum.upcoming, 20, 50, 130, "Rs. 200", 150,
     "Graduation", "21-38", "Odisha Civil Service combined competitive examination."),
    ("jharkhand", "JPSC Combined Civil Services 2026", "jpsc-combined-2026",
     "Administration", StatusEnum.open, -14, 16, 88, "Rs. 600", 210,
     "Graduation", "21-40", "Combined Civil Services exam for Jharkhand state administrative posts."),
    ("chhattisgarh", "CGPSC State Service Exam 2026", "cgpsc-state-service-2026",
     "Administration", StatusEnum.closing_soon, -19, 6, 78, "Rs. 300", 170,
     "Graduation", "21-40", "State Service Examination for Chhattisgarh administrative posts."),
    ("haryana", "HPSC HCS 2026", "hpsc-hcs-2026",
     "Administration", StatusEnum.open, -10, 20, 92, "Rs. 500", 95,
     "Graduation", "21-42", "Haryana Civil Services combined competitive examination."),
    ("himachal-pradesh", "HPPSC Allied Services 2026", "hppsc-allied-2026",
     "Administration", StatusEnum.upcoming, 12, 42, 105, "Rs. 400", 65,
     "Graduation", "21-35", "Himachal Pradesh Allied Services combined competitive examination."),
    ("assam", "APSC CCE 2026", "apsc-cce-2026",
     "Administration", StatusEnum.open, -16, 14, 82, "Rs. 220", 140,
     "Graduation", "21-38", "Combined Competitive Examination for Assam state civil services."),
    ("delhi", "DSSSB PGT Teacher 2026", "dsssb-pgt-2026",
     "Teaching", StatusEnum.closing_soon, -17, 7, 55, "Rs. 100", 850,
     "Postgraduate + B.Ed", "18-30", "Post Graduate Teacher recruitment across Delhi government schools."),
    ("puducherry", "Puducherry PSC Group A 2026", "py-psc-group-a-2026",
     "Administration", StatusEnum.upcoming, 25, 55, 125, "Rs. 200", 30,
     "Graduation", "21-35", "Group A services recruitment for Puducherry administration."),
    ("uttarakhand", "UKPSC Combined State Civil 2026", "ukpsc-combined-2026",
     "Administration", StatusEnum.open, -11, 19, 96, "Rs. 300", 75,
     "Graduation", "21-42", "Combined State Civil/Upper Subordinate Services exam for Uttarakhand."),
    ("tripura", "TPSC Combined Competitive 2026", "tpsc-combined-2026",
     "Administration", StatusEnum.upcoming, 18, 48, 118, "Rs. 150", 40,
     "Graduation", "18-40", "Combined Competitive Examination for Tripura state civil services."),
    ("manipur", "Manipur PSC Combined Competitive 2026", "mpsc-manipur-combined-2026",
     "Administration", StatusEnum.closing_soon, -13, 8, 70, "Rs. 200", 35,
     "Graduation", "21-38", "Combined Competitive Examination for Manipur state civil services."),
]

for state_slug, title, slug_suffix, cat_key, status, start_off, end_off, exam_off, fee, vac, qual, age, desc in MORE_EXAMS:
    org_slug = f"{state_slug}-psc"
    exams.append(Exam(
        title=title, slug=slug_suffix,
        organization_id=orgs[org_slug].id, state_id=states[state_slug].id,
        qualification=qual, age_limit=age,
        application_start_date=d(start_off), application_end_date=d(end_off),
        exam_date=d(exam_off), application_fee=fee,
        status=status, vacancies=vac,
        short_description=desc,
        notification_pdf_url=STATE_PSCS[state_slug][1],
        apply_online_url=STATE_PSCS[state_slug][1],
        official_source_url=STATE_PSCS[state_slug][1], is_verified=True,
        last_verified_at=datetime.utcnow(),
        categories=[categories[cat_key]],
    ))

db.add_all(exams)
db.commit()
db.close()

print("Seed complete:")
print(f"  States + UTs: {len(states)}")
print(f"  Organizations: {len(orgs)}")
print(f"  Categories: {len(categories)}")
print(f"  Exams: {len(exams)}")
