-- =====================================================
-- EuroStyle Fashion - HR Database Initialization
-- =====================================================
-- Creates the eurostyle_hr database and all tables
-- for European employment law compliant HR management

-- Create the HR database
CREATE DATABASE IF NOT EXISTS eurostyle_hr;

-- Use the database for subsequent table creation
USE eurostyle_hr;

-- =====================================================
-- 1. DEPARTMENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS departments (
    department_id String,               -- DEPT_NL_001, DEPT_DE_001
    department_code String,             -- IT, HR, FIN, OPS, RETAIL
    department_name String,             -- Information Technology
    entity_id String,                   -- FK to finance.legal_entities
    parent_department_id Nullable(String), -- FK to parent department
    manager_employee_id Nullable(String),  -- FK to employees (circular reference)
    cost_center_id String,              -- FK to finance.cost_centers
    department_type String,             -- CORPORATE, OPERATIONAL, SUPPORT
    location String,                    -- Amsterdam, Berlin, Paris
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY department_id;

-- =====================================================
-- 2. JOB POSITIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS job_positions (
    position_id String,                 -- POS_NL_001, POS_DE_001
    position_code String,               -- DEV_SR, MGR_HR, SPEC_FIN
    position_title String,              -- Senior Software Developer
    department_id String,               -- FK to departments
    reporting_position_id Nullable(String), -- FK to manager position
    position_level String,             -- JUNIOR, SENIOR, MANAGER, DIRECTOR
    employment_type String,             -- FULL_TIME, PART_TIME, CONTRACT, INTERN
    salary_grade String,                -- Grade A, B, C, D, E
    min_salary_eur Decimal64(2),
    max_salary_eur Decimal64(2),
    country_code String,                -- NL, DE, FR, BE, LU
    required_skills Array(String),      -- ['Python', 'SQL', 'Docker']
    education_requirements String,      -- Bachelor's degree or equivalent
    experience_years UInt8,             -- Minimum years experience
    is_remote_eligible Bool,
    travel_percentage UInt8,            -- 0-100% travel required
    is_active Bool,
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY position_id;

-- =====================================================
-- 3. EMPLOYEES TABLE (GDPR Compliant)
-- =====================================================
CREATE TABLE IF NOT EXISTS employees (
    employee_id String,                 -- EMP_000001
    employee_number String,             -- ESLH000001, ESDE000001
    entity_id String,                   -- FK to finance.legal_entities
    
    -- Personal Information (GDPR Protected)
    personal_email String,              -- Masked in non-production
    work_email String,
    title String,                       -- MR, MS, DR
    first_name String,                  -- Masked in non-production
    middle_name Nullable(String),       -- Masked in non-production
    last_name String,                   -- Masked in non-production
    preferred_name Nullable(String),    -- Masked in non-production
    date_of_birth Date,                 -- Masked in non-production
    gender Enum8('MALE' = 1, 'FEMALE' = 2, 'NON_BINARY' = 3, 'PREFER_NOT_TO_SAY' = 4),
    nationality String,                 -- NL, DE, FR, BE, LU
    country_of_birth String,
    marital_status Enum8('SINGLE' = 1, 'MARRIED' = 2, 'DIVORCED' = 3, 'WIDOWED' = 4, 'DOMESTIC_PARTNERSHIP' = 5),
    number_of_dependents UInt8,
    
    -- Contact Information (GDPR Protected)
    phone_mobile String,                -- Masked in non-production
    phone_home Nullable(String),        -- Masked in non-production
    emergency_contact_name String,      -- Masked in non-production
    emergency_contact_phone String,     -- Masked in non-production
    emergency_contact_relationship String, -- SPOUSE, PARENT, SIBLING, FRIEND
    
    -- Address Information (GDPR Protected)
    address_street String,              -- Masked in non-production
    address_city String,
    address_state Nullable(String),
    address_postal_code String,
    address_country String,
    
    -- Legal/Compliance Information (Masked)
    social_security_number String,      -- ***-**-#### format (masked)
    tax_id String,                      -- Partially masked
    passport_number String,             -- Masked
    passport_expiry_date Nullable(Date),
    visa_status Enum8('EU_CITIZEN' = 1, 'WORK_PERMIT' = 2, 'STUDENT_VISA' = 3, 'OTHER' = 4),
    visa_expiry_date Nullable(Date),
    work_permit_required Bool,
    work_permit_expiry_date Nullable(Date),
    
    -- Employment Status
    employee_status Enum8('ACTIVE' = 1, 'INACTIVE' = 2, 'TERMINATED' = 3, 'ON_LEAVE' = 4),
    hire_date Date,
    termination_date Nullable(Date),
    termination_reason Nullable(String),
    rehire_eligible Bool,
    
    -- GDPR Compliance
    gdpr_consent_date Nullable(DateTime),
    data_retention_date Nullable(Date), -- When to delete personal data
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY employee_id;

-- =====================================================
-- 4. EMPLOYMENT CONTRACTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS employment_contracts (
    contract_id String,                 -- CONT_NL_000001
    employee_id String,                 -- FK to employees
    position_id String,                 -- FK to job_positions
    contract_type String,               -- PERMANENT, TEMPORARY, FIXED_TERM
    contract_status String,             -- ACTIVE, EXPIRED, TERMINATED
    start_date Date,
    end_date Nullable(Date),            -- NULL for permanent contracts
    
    -- Compensation
    base_salary_eur Decimal64(2),
    currency String,                    -- EUR
    salary_frequency String,            -- MONTHLY, ANNUAL
    overtime_eligible Bool,
    commission_eligible Bool,
    bonus_eligible Bool,
    
    -- Working Conditions
    working_hours_per_week Decimal32(2), -- 40.0, 32.0 for part-time
    probation_period_months UInt8,      -- 1, 2, 6 months
    notice_period_weeks UInt8,          -- European notice periods
    
    -- European Employment Law Compliance
    country_code String,                -- NL, DE, FR, BE, LU
    annual_leave_days UInt16,           -- Country-specific: NL=25, DE=24, FR=25, BE=20, LU=25
    sick_leave_policy String,           -- Country-specific policies
    works_council_applicable Bool,      -- Germany/Netherlands works councils
    collective_bargaining_agreement Nullable(String), -- CAO reference
    
    -- Contract Terms
    trial_period_days Nullable(UInt16),
    confidentiality_agreement Bool,
    non_compete_agreement Bool,
    non_compete_months Nullable(UInt8),
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY (employee_id, start_date);

-- =====================================================
-- 5. COMPENSATION HISTORY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS compensation_history (
    compensation_id String,             -- COMP_2024_000001
    employee_id String,                 -- FK to employees
    effective_date Date,
    change_reason String,               -- PROMOTION, ANNUAL_REVIEW, MARKET_ADJUSTMENT
    
    -- Salary Changes
    previous_base_salary_eur Nullable(Decimal64(2)),
    new_base_salary_eur Decimal64(2),
    salary_change_percentage Decimal32(2),
    currency String,
    
    -- Additional Compensation
    bonus_amount_eur Nullable(Decimal64(2)),
    commission_rate Nullable(Decimal32(2)),
    equity_grant_value_eur Nullable(Decimal64(2)),
    
    -- Benefits
    health_insurance_contribution_eur Nullable(Decimal64(2)),
    pension_contribution_percentage Nullable(Decimal32(2)),
    other_benefits_eur Nullable(Decimal64(2)),
    
    approved_by String,                 -- Manager employee ID
    hr_approved_by String,              -- HR employee ID
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (employee_id, effective_date);

-- =====================================================
-- 6. LEAVE REQUESTS TABLE (European Compliance)
-- =====================================================
CREATE TABLE IF NOT EXISTS leave_requests (
    leave_request_id String,            -- LEAVE_2024_000001
    employee_id String,                 -- FK to employees
    leave_type String,                  -- ANNUAL, SICK, MATERNITY, PATERNITY, PARENTAL, UNPAID
    start_date Date,
    end_date Date,
    total_days Decimal32(1),            -- 5.0, 2.5 (half days)
    request_date Date,
    
    -- European Leave Types
    sick_leave_type Nullable(String),   -- SHORT_TERM, LONG_TERM, CHRONIC
    parental_leave_type Nullable(String), -- MATERNITY, PATERNITY, ADOPTION, CARE
    special_leave_type Nullable(String),  -- BEREAVEMENT, WEDDING, MILITARY
    
    -- Status and Approval
    status String,                      -- PENDING, APPROVED, REJECTED, CANCELLED
    requested_by String,                -- Employee ID
    approved_by Nullable(String),       -- Manager employee ID
    approval_date Nullable(Date),
    rejection_reason Nullable(String),
    
    -- Medical Certification (if required)
    medical_certificate_required Bool,
    medical_certificate_provided Bool,
    doctor_name Nullable(String),       -- GDPR protected
    
    -- European Compliance Notes
    statutory_entitlement Bool,         -- Required by law vs. company policy
    paid_leave Bool,                    -- Full pay, partial pay, unpaid
    pay_percentage Decimal32(2),        -- 100.0, 70.0, 0.0
    
    comments Nullable(String),
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (employee_id, start_date);

-- =====================================================
-- 7. LEAVE BALANCES TABLE (European Compliance)
-- =====================================================
CREATE TABLE IF NOT EXISTS leave_balances (
    balance_id String,                  -- BAL_2024_EMP_000001_ANNUAL
    employee_id String,                 -- FK to employees
    leave_type String,                  -- ANNUAL, SICK, COMP_TIME
    balance_year UInt16,                -- 2024
    
    -- Balance Tracking
    opening_balance Decimal32(1),       -- Start of year balance
    accrued_days Decimal32(1),          -- Earned during year
    used_days Decimal32(1),             -- Taken during year
    expired_days Decimal32(1),          -- Lost due to expiry
    current_balance Decimal32(1),       -- Current available balance
    
    -- European Compliance
    statutory_minimum Decimal32(1),     -- Legal minimum entitlement
    company_entitlement Decimal32(1),   -- Company policy entitlement
    max_carryover Decimal32(1),         -- Maximum days that can carry over
    expiry_date Nullable(Date),         -- When unused days expire
    
    -- Special Balances
    sick_leave_unlimited Bool,          -- Germany/Netherlands unlimited sick leave
    long_term_illness_days Nullable(Decimal32(1)), -- Extended illness tracking
    
    last_updated Date,
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY (employee_id, leave_type, balance_year);

-- =====================================================
-- 8. PERFORMANCE CYCLES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS performance_cycles (
    cycle_id String,                    -- PERF_2024_ANNUAL
    cycle_name String,                  -- 2024 Annual Review
    cycle_type String,                  -- ANNUAL, SEMI_ANNUAL, QUARTERLY
    start_date Date,
    end_date Date,
    review_period_start Date,           -- Period being reviewed
    review_period_end Date,
    status String,                      -- PLANNING, ACTIVE, COMPLETED
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY cycle_id;

-- =====================================================
-- 9. PERFORMANCE REVIEWS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS performance_reviews (
    review_id String,                   -- REV_2024_000001
    cycle_id String,                    -- FK to performance_cycles
    employee_id String,                 -- FK to employees
    reviewer_employee_id String,        -- FK to employees (manager)
    
    -- Review Scores (1-5 scale)
    overall_rating Decimal32(1),        -- 4.2
    goal_achievement_rating Decimal32(1),
    competency_rating Decimal32(1),
    leadership_rating Nullable(Decimal32(1)), -- For leadership positions
    
    -- Goals and Development
    goals_met UInt8,                    -- Number of goals achieved
    total_goals UInt8,                  -- Total number of goals
    development_needs Array(String),    -- ['Communication', 'Technical Skills']
    strengths Array(String),            -- ['Problem Solving', 'Teamwork']
    
    -- Comments
    employee_self_assessment String,
    manager_comments String,
    development_plan String,
    
    -- Review Process
    review_status String,               -- DRAFT, SUBMITTED, APPROVED, COMPLETED
    self_assessment_date Nullable(Date),
    manager_review_date Nullable(Date),
    hr_approval_date Nullable(Date),
    employee_acknowledgment_date Nullable(Date),
    
    -- Outcomes
    promotion_recommended Bool,
    salary_increase_recommended Bool,
    recommended_increase_percentage Nullable(Decimal32(2)),
    pip_recommended Bool,               -- Performance Improvement Plan
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (cycle_id, employee_id);

-- =====================================================
-- 10. TRAINING PROGRAMS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS training_programs (
    program_id String,                  -- TRAIN_TECH_001, TRAIN_MGMT_001
    program_name String,                -- Advanced Python Development
    program_category String,            -- TECHNICAL, LEADERSHIP, COMPLIANCE, SOFT_SKILLS
    program_type String,                -- ONLINE, CLASSROOM, WORKSHOP, CERTIFICATION
    provider_name String,               -- Internal, LinkedIn Learning, Coursera
    duration_hours UInt16,              -- 40 hours
    cost_per_participant_eur Decimal64(2),
    max_participants Nullable(UInt16),
    
    -- Prerequisites and Target Audience
    target_positions Array(String),     -- ['Software Developer', 'Senior Developer']
    prerequisites String,
    skill_level String,                 -- BEGINNER, INTERMEDIATE, ADVANCED
    
    -- Compliance Training
    mandatory Bool,                     -- Required by law/policy
    compliance_type Nullable(String),   -- GDPR, SAFETY, ANTI_DISCRIMINATION
    renewal_required Bool,
    renewal_period_months Nullable(UInt16),
    
    is_active Bool,
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY program_id;

-- =====================================================
-- 11. EMPLOYEE TRAINING TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS employee_training (
    training_record_id String,          -- TRAIN_REC_000001
    employee_id String,                 -- FK to employees
    program_id String,                  -- FK to training_programs
    enrollment_date Date,
    start_date Date,
    completion_date Nullable(Date),
    
    -- Training Results
    status String,                      -- ENROLLED, IN_PROGRESS, COMPLETED, CANCELLED, FAILED
    score Nullable(Decimal32(1)),       -- 85.5% or 4.2/5.0
    certification_earned Bool,
    certification_number Nullable(String),
    certification_expiry_date Nullable(Date),
    
    -- Training Details
    instructor_name Nullable(String),
    training_location Nullable(String), -- ONLINE, Amsterdam Office, External
    cost_eur Decimal64(2),
    approved_by String,                 -- Manager employee ID
    
    -- Feedback
    employee_feedback Nullable(String),
    employee_rating Nullable(UInt8),    -- 1-5 stars
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (employee_id, enrollment_date);

-- =====================================================
-- 12. EMPLOYEE SURVEYS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS employee_surveys (
    survey_id String,                   -- SURV_2024_ENGAGEMENT
    survey_name String,                 -- 2024 Employee Engagement Survey
    survey_type String,                 -- ENGAGEMENT, EXIT, ONBOARDING, PULSE
    start_date Date,
    end_date Date,
    target_audience String,             -- ALL_EMPLOYEES, MANAGERS, DEPARTMENT_SPECIFIC
    is_anonymous Bool,                  -- GDPR consideration
    response_rate_target Decimal32(2),  -- 85.0%
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_date)
ORDER BY survey_id;

-- =====================================================
-- 13. SURVEY RESPONSES TABLE (GDPR Compliant)
-- =====================================================
CREATE TABLE IF NOT EXISTS survey_responses (
    response_id String,                 -- RESP_2024_000001
    survey_id String,                   -- FK to employee_surveys
    employee_id Nullable(String),       -- FK to employees (NULL if anonymous)
    response_date DateTime,
    
    -- Response Data (Anonymized/Aggregated)
    overall_satisfaction UInt8,         -- 1-10 scale
    work_life_balance_rating UInt8,     -- 1-10 scale
    compensation_satisfaction UInt8,    -- 1-10 scale
    career_development_rating UInt8,    -- 1-10 scale
    management_effectiveness UInt8,     -- 1-10 scale
    company_culture_rating UInt8,       -- 1-10 scale
    
    -- Open-ended Responses (Anonymized)
    likes_most String,                  -- What do you like most?
    improvement_suggestions String,     -- What could be improved?
    additional_comments String,
    
    -- Demographics (for analysis)
    department_group Nullable(String),  -- Anonymized department grouping
    tenure_group Nullable(String),      -- 0-1yr, 1-3yr, 3-5yr, 5+yr
    age_group Nullable(String),         -- 20-30, 30-40, 40-50, 50+
    role_level Nullable(String),        -- INDIVIDUAL, MANAGER, DIRECTOR
    
    -- GDPR Compliance
    consent_given Bool,                 -- Explicit consent for data processing
    anonymization_level String,        -- FULL, PARTIAL, IDENTIFIABLE
    
    created_date DateTime,
    updated_date DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (survey_id, response_date);

-- =====================================================
-- HR DATABASE SETUP COMPLETE
-- =====================================================
-- The eurostyle_hr database has been created with:
-- - 13 comprehensive HR tables
-- - European employment law compliance (NL, DE, FR, BE, LU)
-- - GDPR data protection and privacy controls
-- - Comprehensive leave management with statutory compliance
-- - Performance management and career development tracking
-- - Training and development program management
-- - Employee engagement and survey capabilities
-- - Proper ClickHouse engines optimized for HR data patterns