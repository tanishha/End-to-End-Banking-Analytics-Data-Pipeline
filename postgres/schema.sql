CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    member_id INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    policy_type VARCHAR(50) NOT NULL,      -- HMO | PPO | EPO | Medicare | Medicaid
    coverage_amount NUMERIC(18,2) NOT NULL CHECK (coverage_amount >= 0),
    premium_amount NUMERIC(10,2) NOT NULL CHECK (premium_amount >= 0),
    policy_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | LAPSED | TERMINATED
    start_date DATE NOT NULL,
    end_date DATE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


CREATE TABLE IF NOT EXISTS claims (
    id BIGSERIAL PRIMARY KEY,
    policy_id INT NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    claim_type VARCHAR(50) NOT NULL,     -- MEDICAL | DENTAL | PHARMACY
    claim_amount NUMERIC(18,2) NOT NULL CHECK (claim_amount > 0),
    approved_amount NUMERIC(18,2) DEFAULT 0 CHECK (approved_amount >= 0),
    claim_status VARCHAR(20) NOT NULL DEFAULT 'SUBMITTED',  
        -- SUBMITTED | APPROVED | REJECTED | PAID
    service_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Simple indexed columns for performance in queries
CREATE INDEX IF NOT EXISTS idx_claims_policy_created 
ON claims(policy_id, created_at);