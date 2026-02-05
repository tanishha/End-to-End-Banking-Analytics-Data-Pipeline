{% snapshot members_snapshot %}
{{
    config(
      target_schema='ANALYTICS',
      unique_key='member_id',
      strategy='check',
      check_cols=['first_name', 'last_name', 'email', 'date_of_birth']
    )
}}
SELECT
    id as member_id,
    first_name,
    last_name,
    email,
    date_of_birth,
    created_at
FROM {{ source('raw', 'members') }}
{% endsnapshot %}
