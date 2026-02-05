SELECT
    cl.claim_id,
    cl.policy_id,
    m.member_id,
    cl.claim_amount,
    cl.approved_amount,
    cl.claim_status,
    cl.claim_type,
    cl.service_date,
    CURRENT_TIMESTAMP AS load_timestamp
FROM {{ ref('stg_claims') }} cl
LEFT JOIN {{ ref('dim_policies') }} p
    ON cl.policy_id = p.policy_id
    AND cl.service_date >= p.effective_from
    AND (cl.service_date < p.effective_to OR p.effective_to IS NULL)
LEFT JOIN {{ ref('dim_members') }} m
    ON p.member_id = m.member_id
    AND cl.service_date >= m.effective_from
    AND (cl.service_date < m.effective_to OR m.effective_to IS NULL)