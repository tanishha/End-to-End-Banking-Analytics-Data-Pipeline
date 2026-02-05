import time
import psycopg2
from decimal import Decimal, ROUND_DOWN
from faker import Faker
import random
import argparse
import sys
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

# -----------------------------
# Project configuration
# -----------------------------
NUM_MEMBERS = 10
POLICIES_PER_MEMBER = 1
NUM_CLAIMS = 50

# Coverage / premium ranges
COVERAGE_MIN = Decimal("5000.00")
COVERAGE_MAX = Decimal("200000.00")
PREMIUM_MIN = Decimal("50.00")
PREMIUM_MAX = Decimal("1200.00")

# Claim ranges
CLAIM_MIN = Decimal("10.00")
CLAIM_MAX = Decimal("5000.00")

# Loop config
DEFAULT_LOOP = True
MAX_ITERATIONS = 100
SLEEP_SECONDS = 2

# CLI override (run once mode)
parser = argparse.ArgumentParser(description="Run fake healthcare insurance data generator")
parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
args = parser.parse_args()
LOOP = not args.once and DEFAULT_LOOP

# -----------------------------
# Helpers
# -----------------------------
fake = Faker()

POLICY_TYPES = ["HMO", "PPO", "EPO", "Medicare", "Medicaid"]
POLICY_STATUSES = ["ACTIVE", "LAPSED", "TERMINATED"]
CLAIM_TYPES = ["MEDICAL", "DENTAL", "PHARMACY"]
CLAIM_STATUSES = ["SUBMITTED", "APPROVED", "REJECTED", "PAID"]

def random_money(min_val: Decimal, max_val: Decimal) -> Decimal:
    val = Decimal(str(random.uniform(float(min_val), float(max_val))))
    return val.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def random_dob(min_age: int = 0, max_age: int = 90) -> date:
    """Return a DOB such that age is between min_age and max_age."""
    today = date.today()
    start = today - timedelta(days=max_age * 365)
    end = today - timedelta(days=min_age * 365)
    # Faker date_between takes strings or dates
    return fake.date_between(start_date=start, end_date=end)

def random_policy_dates() -> tuple[date, date | None]:
    """Policy start date within last 5 years. End date optional."""
    today = date.today()
    start = fake.date_between(start_date=today - timedelta(days=5 * 365), end_date=today)
    # 30% chance of end_date set (terminated/lapsed)
    if random.random() < 0.30:
        end = fake.date_between(start_date=start, end_date=today)
        return start, end
    return start, None

def derive_premium(policy_type: str, coverage_amount: Decimal) -> Decimal:
    """Simple rule-based premium so data looks consistent."""
    base = {
        "HMO": Decimal("0.0030"),
        "PPO": Decimal("0.0040"),
        "EPO": Decimal("0.0035"),
        "Medicare": Decimal("0.0020"),
        "Medicaid": Decimal("0.0015"),
    }[policy_type]
    premium = (coverage_amount * base).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    # clamp to configured range
    if premium < PREMIUM_MIN:
        premium = PREMIUM_MIN
    if premium > PREMIUM_MAX:
        premium = PREMIUM_MAX
    return premium

def choose_policy_status(end_date: date | None) -> str:
    if end_date is None:
        return "ACTIVE"
    return random.choice(["LAPSED", "TERMINATED"])

def service_date_within_policy(start_date: date, end_date: date | None) -> date:
    today = date.today()
    upper = end_date if end_date else today
    if upper < start_date:
        upper = start_date
    return fake.date_between(start_date=start_date, end_date=upper)

def claim_outcome(claim_amount: Decimal) -> tuple[str, Decimal]:
    """
    Determine status + approved_amount with basic realism:
    - REJECTED: approved_amount = 0
    - APPROVED: approved_amount <= claim_amount
    - PAID: approved_amount <= claim_amount
    - SUBMITTED: approved_amount = 0 (unknown yet)
    """
    status = random.choices(
        population=["SUBMITTED", "APPROVED", "REJECTED", "PAID"],
        weights=[0.35, 0.25, 0.15, 0.25],
        k=1,
    )[0]

    if status in ["SUBMITTED", "REJECTED"]:
        return status, Decimal("0.00")

    # APPROVED or PAID
    approved = random_money(Decimal("1.00"), claim_amount)
    return status, approved

# -----------------------------
# Connect to Postgres
# -----------------------------
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
conn.autocommit = True
cur = conn.cursor()

# -----------------------------
# Core generation logic (one iteration)
# -----------------------------
def run_iteration():
    members = []

    # 1. Generate members
    for _ in range(NUM_MEMBERS):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        dob = random_dob(min_age=0, max_age=85)

        cur.execute(
            """
            INSERT INTO members (first_name, last_name, email, date_of_birth)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (first_name, last_name, email, dob),
        )
        member_id = cur.fetchone()[0]
        members.append(member_id)

    # 2. Generate policies
    policies = []  # list of tuples: (policy_id, start_date, end_date, coverage_amount)
    for member_id in members:
        for _ in range(POLICIES_PER_MEMBER):
            policy_type = random.choice(POLICY_TYPES)
            coverage_amount = random_money(COVERAGE_MIN, COVERAGE_MAX)
            premium_amount = derive_premium(policy_type, coverage_amount)

            start_date, end_date = random_policy_dates()
            policy_status = choose_policy_status(end_date)

            cur.execute(
                """
                INSERT INTO policies
                    (member_id, policy_type, coverage_amount, premium_amount, policy_status, start_date, end_date)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (member_id, policy_type, coverage_amount, premium_amount, policy_status, start_date, end_date),
            )
            policy_id = cur.fetchone()[0]
            policies.append((policy_id, start_date, end_date, coverage_amount))

    # 3. Generate claims
    for _ in range(NUM_CLAIMS):
        policy_id, start_date, end_date, coverage_amount = random.choice(policies)

        claim_type = random.choice(CLAIM_TYPES)
        service_date = service_date_within_policy(start_date, end_date)

        # Keep claims generally under a reasonable slice of coverage
        max_claim = min(CLAIM_MAX, coverage_amount)
        claim_amount = random_money(CLAIM_MIN, max_claim)

        claim_status, approved_amount = claim_outcome(claim_amount)

        cur.execute(
            """
            INSERT INTO claims
                (policy_id, claim_type, claim_amount, approved_amount, claim_status, service_date)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (policy_id, claim_type, claim_amount, approved_amount, claim_status, service_date),
        )

    print(
        f"Generated {len(members)} members, {len(policies)} policies, {NUM_CLAIMS} claims."
    )

try:
    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n--- Iteration {iteration}/{MAX_ITERATIONS} started ---")
        run_iteration()
        print(f"--- Iteration {iteration}/{MAX_ITERATIONS} finished ---")
        if not LOOP:
            break
        time.sleep(SLEEP_SECONDS)

    print(f"\nCompleted {iteration} iterations. Exiting...")

except KeyboardInterrupt:
    print("\nInterrupted by user. Exiting gracefully...")

finally:
    cur.close()
    conn.close()
    sys.exit(0)
