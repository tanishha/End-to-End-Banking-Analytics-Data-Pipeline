select
    id as member_id,
    first_name,
    last_name,
    email,
    date_of_birth,
    created_at,
    current_timestamp as load_timestamp
from {{ source('raw', 'members') }}
