WITH source_data AS (
    SELECT
        policy_id,
        member_id,
        policy_type,
        coverage_amount,
        premium_amount,
        policy_status,
        start_date,
        end_date,
        created_at,
        dbt_valid_from   AS effective_from,
        dbt_valid_to     AS effective_to,
        CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current
    FROM {{ ref('policies_snapshot') }}
)

SELECT * FROM source_data