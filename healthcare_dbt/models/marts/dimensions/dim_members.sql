WITH latest AS (
    SELECT
        member_id,
        first_name,
        last_name,
        email,
        date_of_birth,
        created_at,
        dbt_valid_from   AS effective_from,
        dbt_valid_to     AS effective_to,
        CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current
    FROM {{ ref('members_snapshot') }}
)

SELECT * FROM latest