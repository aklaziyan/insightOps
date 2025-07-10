CREATE TABLE credit_application (
    report_date                  timestamp       NOT NULL,
    report_country               varchar(50)     NOT NULL,
    report_portfolio             varchar(50)     NOT NULL,
    tx_id                        varchar(64)     PRIMARY KEY,
    application_date             timestamp       NOT NULL,
    main_channel                 varchar(50)     NOT NULL,
    subchannels                  varchar(50),
    purpose_of_loan              varchar(50)     NOT NULL,
    credit_bureau_null_flag      smallint        NOT NULL,
    internal_model_score         decimal(10,4)   NOT NULL,
    expected_pd                  decimal(10,4),
    policy_rules_flag            smallint        NOT NULL,
    other_rule_flag              smallint        NOT NULL,
    fraud_rule_flag              smallint        NOT NULL,
    score_decline_flag           decimal(10,4),
    application_status           varchar(50)     NOT NULL,
    credit_bureau_query          varchar(100),
    credit_bureau_score          decimal(10,4),
    all_credit_bureau_raw_fields text,
    other_credit_bureau_scores   decimal(10,4),
    rule_details                 text,
    affordability_flag           smallint        NOT NULL,
    net_income                   decimal(10,4)   NOT NULL,
    net_expenditure              varchar(100),
    branch_id                    varchar(64),
    branch_name                  varchar(100),
    region_name                  varchar(100),
    cash_collateral              varchar(100),
    time_with_bank               timestamp,
    auto_decision_flag           smallint        NOT NULL,
    application_tenor            varchar(100),
    application_amount           decimal(10,4)   NOT NULL,
    approved_date                timestamp,
    approved_tenor               varchar(100),
    approved_amount              decimal(10,4),
    disbursed_date               timestamp,
    disbursed_tenor              varchar(100),
    disbursed_amount             decimal(10,4),
    postponment_flag             smallint,
    postponment_month            varchar(100),
    equal_installment_flag       varchar(64),
    work_type                    varchar(50),
    working_sector               varchar(100),
    decision_engine_name         varchar(100),
    credit_card_flag             smallint,
    credit_card_limit            decimal(10,4),
    overdraft_flag               smallint,
    overdraft_limit              decimal(10,4),
    car_loan_flag                smallint,
    car_loan_amount              decimal(10,4),
    mortgage_flag                smallint,
    mortgage_amount              decimal(10,4),
    model_drivers                decimal(10,4),
    rule_drivers                 decimal(10,4),
    utm_source                   varchar(100),
    manual_underwriter_id        varchar(64),
    affordability_reason         varchar(50),
    applicant_age                integer,
    applicant_gender             varchar(100),
    interest_rate                decimal(10,4)   NOT NULL,
    margin                       decimal(10,4),
    fee_amount                   decimal(10,4),
    pre_approved_last_valid_date timestamp,
    currency                     varchar(10)     NOT NULL,
    salary_customer_flag         smallint        NOT NULL,
    existing_customer_flag       smallint        NOT NULL
);

-- Alan açıklamaları (COMMENT komutları)
COMMENT ON COLUMN credit_application.report_date                  IS 'Date on which report is generated.';
COMMENT ON COLUMN credit_application.report_country               IS 'Country for this report.';
COMMENT ON COLUMN credit_application.report_portfolio             IS 'Portfolio for which report is being generated.';
COMMENT ON COLUMN credit_application.tx_id                        IS 'Transaction ID. Unique application identifier.';
COMMENT ON COLUMN credit_application.application_date             IS 'Date of the application for the financial product.';
COMMENT ON COLUMN credit_application.main_channel                 IS 'Main channel via which application was made.';
COMMENT ON COLUMN credit_application.subchannels                  IS 'Sub-channel (if exists).';
COMMENT ON COLUMN credit_application.purpose_of_loan              IS 'Purpose of the loan.';
COMMENT ON COLUMN credit_application.credit_bureau_null_flag      IS '1 if applicant has no Credit Bureau Data, 0 otherwise.';
COMMENT ON COLUMN credit_application.internal_model_score         IS 'Internal model score assigned to the applicant.';
COMMENT ON COLUMN credit_application.expected_pd                  IS 'Expected probability of default (PD) for the internal model.';
COMMENT ON COLUMN credit_application.policy_rules_flag            IS '1 if applicant hits global policy rules, 0 otherwise.';
COMMENT ON COLUMN credit_application.other_rule_flag              IS '1 if applicant hits other rules, 0 otherwise.';
COMMENT ON COLUMN credit_application.fraud_rule_flag              IS '1 if applicant hits any fraud rule, 0 otherwise.';
COMMENT ON COLUMN credit_application.score_decline_flag           IS '1 if rejected due to score cut-off, 0 otherwise.';
COMMENT ON COLUMN credit_application.application_status           IS 'Application status: Rejected, Accepted, Disbursed, In Process.';
COMMENT ON COLUMN credit_application.credit_bureau_query          IS '0 if call to credit bureau was successful, -99 if failed, 1 for partial success.';
COMMENT ON COLUMN credit_application.credit_bureau_score          IS 'Credibility score from credit bureau.';
COMMENT ON COLUMN credit_application.all_credit_bureau_raw_fields IS 'Credit bureau raw fields for every application.';
COMMENT ON COLUMN credit_application.other_credit_bureau_scores   IS 'Other scores from credit bureau data, if present.';
COMMENT ON COLUMN credit_application.rule_details                 IS 'All the rules in the system hit, separated by ;';
COMMENT ON COLUMN credit_application.affordability_flag           IS '1 if application is rejected for affordability, 0 otherwise.';
COMMENT ON COLUMN credit_application.net_income                   IS 'Net income of the applicant.';
COMMENT ON COLUMN credit_application.net_expenditure              IS 'Net expenditure of the applicant.';
COMMENT ON COLUMN credit_application.branch_id                    IS 'Branch ID (if application is from branch).';
COMMENT ON COLUMN credit_application.branch_name                  IS 'Branch name (if application is from branch).';
COMMENT ON COLUMN credit_application.region_name                  IS 'Region name (if application is from branch).';
COMMENT ON COLUMN credit_application.cash_collateral              IS 'If loan is disbursed with cash collateral, this field shows amount.';
COMMENT ON COLUMN credit_application.time_with_bank               IS 'Date of BANK account opening.';
COMMENT ON COLUMN credit_application.auto_decision_flag           IS '1 if auto decision, 0 if manual.';
COMMENT ON COLUMN credit_application.application_tenor            IS 'Requested loan tenor.';
COMMENT ON COLUMN credit_application.application_amount           IS 'Requested loan amount.';
COMMENT ON COLUMN credit_application.approved_date                IS 'Date of approval if application is approved.';
COMMENT ON COLUMN credit_application.approved_tenor               IS 'Approved tenure if application is approved.';
COMMENT ON COLUMN credit_application.approved_amount              IS 'Approved amount if application is approved.';
COMMENT ON COLUMN credit_application.disbursed_date               IS 'Date of disbursement if loan is disbursed.';
COMMENT ON COLUMN credit_application.disbursed_tenor              IS 'Disbursed tenure if loan is disbursed.';
COMMENT ON COLUMN credit_application.disbursed_amount             IS 'Disbursed loan amount if loan is disbursed.';
COMMENT ON COLUMN credit_application.postponment_flag             IS 'If the first installment has been postponed, 1 else 0.';
COMMENT ON COLUMN credit_application.postponment_month            IS 'If first installment is postponed, which month.';
COMMENT ON COLUMN credit_application.equal_installment_flag       IS '1 if equal installment loan, 0 otherwise.';
COMMENT ON COLUMN credit_application.work_type                    IS 'Applicant''s working type (retired, self employed, etc.).';
COMMENT ON COLUMN credit_application.working_sector               IS 'If self-employed, sector name.';
COMMENT ON COLUMN credit_application.decision_engine_name         IS 'Name of decision engine model used.';
COMMENT ON COLUMN credit_application.credit_card_flag             IS '1 if applicant has credit card, else 0.';
COMMENT ON COLUMN credit_application.credit_card_limit            IS 'Credit card limit.';
COMMENT ON COLUMN credit_application.overdraft_flag               IS '1 if applicant has overdraft, else 0.';
COMMENT ON COLUMN credit_application.overdraft_limit              IS 'Overdraft limit.';
COMMENT ON COLUMN credit_application.car_loan_flag                IS '1 if applicant has car loan, else 0.';
COMMENT ON COLUMN credit_application.car_loan_amount              IS 'Disbursed amount if applicant has car loan.';
COMMENT ON COLUMN credit_application.mortgage_flag                IS '1 if applicant has mortgage, else 0.';
COMMENT ON COLUMN credit_application.mortgage_amount              IS 'Disbursed amount if applicant has mortgage.';
COMMENT ON COLUMN credit_application.model_drivers                IS 'Model drivers and their values (if available).';
COMMENT ON COLUMN credit_application.rule_drivers                 IS 'All rule drivers and their values (if available).';
COMMENT ON COLUMN credit_application.utm_source                   IS 'Channel application source (UTM, etc.).';
COMMENT ON COLUMN credit_application.manual_underwriter_id        IS 'ID of manual underwriter if applicable.';
COMMENT ON COLUMN credit_application.affordability_reason         IS 'Affordability failure reason/component.';
COMMENT ON COLUMN credit_application.applicant_age                IS 'Applicant age (integer).';
COMMENT ON COLUMN credit_application.applicant_gender             IS 'Applicant gender.';
COMMENT ON COLUMN credit_application.interest_rate                IS 'Interest rate.';
COMMENT ON COLUMN credit_application.margin                       IS 'Loan margin rate.';
COMMENT ON COLUMN credit_application.fee_amount                   IS 'Loan fee amount (application fee/commission).';
COMMENT ON COLUMN credit_application.pre_approved_last_valid_date IS 'If preapproved loan, last valid date to use automatically.';
COMMENT ON COLUMN credit_application.currency                     IS 'Currency of application.';
COMMENT ON COLUMN credit_application.salary_customer_flag         IS '1 if customer is a salary customer, 0 otherwise.';
COMMENT ON COLUMN credit_application.existing_customer_flag       IS '1 if customer is an existing customer, 0 otherwise.';
