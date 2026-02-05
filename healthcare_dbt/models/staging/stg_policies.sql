select
    id as policy_id,
    member_id,
    policy_type,
    coverage_amount,
    premium_amount,
    policy_status,
    start_date,
    end_date,
    created_at,
    current_timestamp as load_timestamp
from {{ source('raw', 'policies') }}
