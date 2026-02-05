select
    id as claim_id,
    policy_id,
    claim_amount,
    approved_amount,
    claim_type,
    claim_status,
    service_date,
    created_at as claim_created_at,
    current_timestamp as load_timestamp
from {{ source('raw', 'claims') }}
