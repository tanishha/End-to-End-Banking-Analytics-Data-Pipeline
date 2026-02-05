{% snapshot policies_snapshot %}
{{
    config(
      target_schema='ANALYTICS',
      unique_key='policy_id',
      strategy='check',
      check_cols=['policy_type', 'coverage_amount', 'premium_amount', 'policy_status', 'start_date', 'end_date']
    )
}}
SELECT
    id as policy_id,
    member_id,
    policy_type,
    coverage_amount,
    premium_amount,
    policy_status,
    start_date,
    end_date,
    created_at
FROM {{ source('raw', 'policies') }}
{% endsnapshot %}
