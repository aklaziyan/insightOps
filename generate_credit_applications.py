import psycopg2
from faker import Faker
import random
import numpy as np
from datetime import datetime, timedelta

DB_NAME = "insightops"
DB_USER = "insightops"
DB_PASS = "insightops"
DB_HOST = "localhost"
DB_PORT = 5432

N = 10000  # Kaç kayıt eklenecek?

fake = Faker()
random.seed(42)
np.random.seed(42)

portfolio_choices = (["CF"] * 5000 + ["PF"] * 2500 + ["AF"] * 1500 + ["CORP"] * 500 + ["MORTGAGE"] * 500)
random.shuffle(portfolio_choices)

main_channel_map = {
    "CF": (["POS"] * 50 + ["Mobile"] * 20 + ["Public Web"] * 10 + ["Preapproved"] * 10 + ["Call Center"] * 10),
    "PF": (["Mobile"] * 35 + ["Public Web"] * 30 + ["Call Center"] * 20 + ["Preapproved"] * 10 + ["Branch"] * 5),
    "AF": (["Branch"] * 80 + ["POS"] * 20),
    "CORP": (["Branch"] * 100),
    "MORTGAGE": (["Branch"] * 100),
}

subchannels_map = {
    "POS": ["Electronics", "Home Furnishing", "Automotive", "Telecom", "White Goods"],
    "Public Web": ["Landing Page", "Comparison Site", "Referral"],
    "Mobile": ["App", "Mobile Web"],
}

purpose_map = {
    "CF": ["Home Renovation", "Vacation", "Wedding", "Education", "Debt Consolidation", "Medical", "Electronics", "General Needs", "Home Furnishing"],
    "PF": ["Home Renovation", "Vacation", "Wedding", "Education", "Debt Consolidation", "Medical", "Electronics", "General Needs", "Home Furnishing"],
    "AF": ["Vehicle Purchase", "Car Renewal", "Fleet Leasing", "Second-hand Car", "Motorcycle"],
    "MORTGAGE": ["First Home Purchase", "Home Renovation", "Mortgage Refinancing", "Second Home Purchase"],
    "CORP": ["Machinery Investment", "Working Capital", "Office Equipment", "Fleet Expansion", "Commercial Real Estate"],
}

regions = ["Marmara1"]*10 + ["Marmara2"]*7 + ["Ege1"]*6 + ["Ege2"]*5 + ["İç Anadolu1"]*6 + ["İç Anadolu2"]*5 + ["Akdeniz"]*4 + ["Karadeniz"]*3 + ["Doğu Anadolu"]*2 + ["Güneydoğu Anadolu"]*2
branch_ids = [f"BRANCH{str(i+1).zfill(2)}" for i in range(50)]
branch_region_map = dict(zip(branch_ids, regions))
branch_names = branch_ids  # branch_id = branch_name

rule_code_options = ["AgeLimit", "ScoreCutoff", "EmploymentCheck", "SectorBlock", "IncomeProof", "FraudAlert", "DebtToIncome", "ManualReview"]
decision_engine_names = ["ScoringV1", "ScoringV2", "DecisionAI2024", "LegacyModel", "ManualReview", "SmartScoreX"]
utm_options = ["GoogleAds", "Facebook", "Organic", "Direct", "Partner", "App Notification", "SMS", "Referral"]

def np_normal_int(mean, std, low, high):
    return int(np.clip(np.random.normal(mean, std), low, high))

def clean_value(x):
    if isinstance(x, (np.int64, np.integer)):
        return int(x)
    if isinstance(x, (np.float64, np.floating)):
        return float(x)
    return x

conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()

today = datetime.now()
rows = []

for i in range(N):
    report_date = today.strftime("%Y-%m-%d %H:%M:%S")
    report_country = "Turkey"
    portfolio = portfolio_choices[i]
    tx_id = f"TX{str(i+1).zfill(7)}"
    application_date = today - timedelta(days=random.randint(0, 730), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    report_portfolio = portfolio

    main_channel = random.choice(main_channel_map[portfolio])
    subchannels = random.choice(subchannels_map[main_channel]) if main_channel in subchannels_map else None
    purpose_of_loan = random.choice(purpose_map[portfolio])
    credit_bureau_null_flag = random.choices([False, True], [0.95, 0.05])[0]
    internal_model_score = round(random.uniform(400, 1000), 4)
    expected_pd = round(np.clip((1.1 - (internal_model_score / 1000)) * random.uniform(0.01, 0.3), 0.01, 0.3), 4)
    policy_rules_flag = random.choices([False, True], [0.97, 0.03])[0]
    other_rule_flag = random.choices([False, True], [0.95, 0.05])[0]
    fraud_rule_flag = random.choices([False, True], [0.99, 0.01])[0]

    app_days_ago = (today - application_date).days
    if app_days_ago <= 7:
        if portfolio in ["CF", "PF"]:
            status_weights = [0.20, 0.40, 0.05, 0.35]
            statuses = ["In Process", "Accepted", "Rejected", "Disbursed"]
        else:
            status_weights = [0.65, 0.25, 0.05, 0.05]
            statuses = ["In Process", "Accepted", "Rejected", "Disbursed"]
    elif 7 < app_days_ago <= 30:
        status_weights = [0.03, 0.10, 0.37, 0.50]
        statuses = ["In Process", "Accepted", "Rejected", "Disbursed"]
    else:
        status_weights = [0.00, 0.05, 0.15, 0.80]
        statuses = ["In Process", "Accepted", "Rejected", "Disbursed"]
    application_status = random.choices(statuses, status_weights)[0]

    score_decline_flag = 1 if application_status == "Rejected" and random.random() < 0.9 else 0
    credit_bureau_query = random.choices(["0", "-99", "1"], [0.97, 0.02, 0.01])[0]
    credit_bureau_score = (round(random.uniform(300, 1900), 4) if credit_bureau_query != "-99" else None)
    all_credit_bureau_raw_fields = 1000 + i
    other_credit_bureau_scores = (round(random.uniform(300, 1900), 4) if random.random() < 0.2 else None)
    rule_details = ";".join(random.sample(rule_code_options, k=random.randint(1, 3))) if random.random() < 0.3 else None
    affordability_flag = random.choices([False, True], [0.90, 0.10])[0]
    if portfolio in ["CF", "PF"]:
        net_income = np_normal_int(250000, 60000, 25000, 250000)
    elif portfolio == "MORTGAGE":
        net_income = np_normal_int(350000, 100000, 100000, 1000000)
    elif portfolio == "CORP":
        net_income = np_normal_int(10000000, 6000000, 1000000, 100000000)
    else:
        net_income = np_normal_int(1500000, 350000, 500000, 7500000)
    net_expenditure = (str(int(net_income * random.uniform(0.3, 0.9))) if random.random() > 0.1 else None)
    if main_channel == "Branch":
        branch_id = random.choice(branch_ids)
        branch_name = branch_id
        region_name = branch_region_map[branch_id]
    else:
        branch_id = branch_name = region_name = None
    cash_collateral = None
    if application_status in ["Disbursed", "Accepted"] and portfolio in ["AF", "MORTGAGE", "CORP"] and random.random() < 0.1:
        cash_collateral = str(np_normal_int(1500000, 500000, 200000, 9000000))
    years_with_bank = random.randint(0, 15)
    time_with_bank = application_date - timedelta(days=years_with_bank * 365)
    if portfolio in ["CF", "PF", "AF"]:
        auto_decision_flag = random.choices([True, False], [0.8, 0.2])[0]
    else:
        auto_decision_flag = random.choices([True, False], [0.2, 0.8])[0]
    if portfolio in ["CF", "PF"]:
        tenors = ["12"] * 50 + ["24"] * 30 + ["36"] * 15 + ["48"] * 5
        application_tenor = random.choice(tenors)
    elif portfolio == "MORTGAGE":
        main_tenors = ["60"] * 35 + ["84"] * 35 + ["120"] * 20 + ["180"] * 10
        application_tenor = random.choice(main_tenors)
        if application_tenor in ["60", "84", "120"] and random.random() < 0.25:
            application_tenor = str(int(application_tenor) + random.choice([12, 24]))
    elif portfolio == "AF":
        tenors = ["24"] * 50 + ["36"] * 30 + ["48"] * 20
        application_tenor = random.choice(tenors)
    else:
        tenors = ["12", "24", "36", "48", "60"]
        application_tenor = random.choice(tenors)
    if portfolio in ["CF", "PF"]:
        application_amount = np_normal_int(250000, 75000, 50000, 1250000)
    elif portfolio == "AF":
        application_amount = np_normal_int(2000000, 750000, 500000, 7500000)
    elif portfolio == "MORTGAGE":
        application_amount = np_normal_int(5000000, 1500000, 1000000, 50000000)
    else:
        application_amount = np_normal_int(10000000, 6000000, 2500000, 125000000)
    if application_status in ["Accepted", "Disbursed"]:
        approved_date = application_date + timedelta(days=random.randint(1, 14))
        approved_tenor = application_tenor
        approved_amount = int(application_amount * random.uniform(0.95, 1))
    else:
        approved_date = approved_tenor = approved_amount = None
    if application_status == "Disbursed":
        disbursed_date = approved_date + timedelta(days=random.randint(1, 10)) if approved_date else None
        disbursed_tenor = approved_tenor
        disbursed_amount = int(approved_amount * random.uniform(0.98, 1)) if approved_amount else None
    else:
        disbursed_date = disbursed_tenor = disbursed_amount = None
    if application_status == "Disbursed" and portfolio in ["AF", "MORTGAGE", "CORP"] and random.random() < 0.1:
        postponment_flag = True
        postponment_month = (disbursed_date + timedelta(days=random.randint(0, 90))).strftime("%Y-%m") if disbursed_date else None
    else:
        postponment_flag = False
        postponment_month = None
    if portfolio in ["CF", "PF"]:
        equal_installment_flag = random.choices([True, False], [0.9, 0.1])[0]
    elif portfolio == "MORTGAGE":
        equal_installment_flag = random.choices([True, False], [0.7, 0.3])[0]
    elif portfolio == "AF":
        equal_installment_flag = random.choices([True, False], [0.7, 0.3])[0]
    else:
        equal_installment_flag = random.choices([True, False], [0.6, 0.4])[0]
    work_type = random.choices(["Employed", "Self Employed", "Retired", "Student", "Unemployed"], [0.65, 0.12, 0.15, 0.05, 0.03])[0]
    if work_type == "Self Employed":
        working_sector = random.choice(["Construction", "IT", "Retail", "Health", "Transport"])
    elif work_type == "Employed":
        sector_kind = random.choices(["Public Sector", "Private Sector"], [0.25, 0.75])[0]
        if sector_kind == "Public Sector":
            working_sector = "Public Sector"
        else:
            working_sector = random.choice(["IT", "Finance", "Retail", "Manufacturing", "Health"])
    else:
        working_sector = None
    decision_engine_name = random.choice(decision_engine_names)
    credit_card_flag = random.choices([True, False], [0.6, 0.4])[0]
    credit_card_limit = int(random.uniform(50000, 750000)) if credit_card_flag else None
    overdraft_flag = random.choices([True, False], [0.3, 0.7])[0]
    overdraft_limit = int(random.uniform(10000, 100000)) if overdraft_flag else None
    if portfolio == "AF":
        car_loan_flag = random.choices([True, False], [0.6, 0.4])[0]
    elif portfolio in ["CF", "PF"]:
        car_loan_flag = random.choices([True, False], [0.05, 0.95])[0]
    else:
        car_loan_flag = random.choices([True, False], [0.02, 0.98])[0]
    car_loan_amount = int(random.uniform(500000, 7000000)) if car_loan_flag else None
    if portfolio == "MORTGAGE":
        mortgage_flag = random.choices([True, False], [0.98, 0.02])[0]
    else:
        mortgage_flag = random.choices([True, False], [0.02, 0.98])[0]
    mortgage_amount = int(random.uniform(1000000, 50000000)) if mortgage_flag else None
    model_drivers = round(random.uniform(0.5, 1.5), 4) if random.random() > 0.2 else None
    rule_drivers = round(random.uniform(0.5, 1.5), 4) if random.random() > 0.2 else None
    if main_channel in ["Public Web", "Mobile"]:
        utm_source = random.choice(utm_options)
    elif main_channel == "POS":
        utm_source = None
    else:
        utm_source = random.choice(["GoogleAds", "Organic", "Referral", "Direct"])
    manual_underwriter_id = random.choice([f"UW{str(j+1).zfill(3)}" for j in range(10)]) if not auto_decision_flag else None
    affordability_reason = random.choice(["LowIncome", "HighExpenses", "ExistingDebt", "NoProof", "Other"]) if affordability_flag else None
    if portfolio in ["CF", "PF"]:
        applicant_age = np_normal_int(35, 10, 18, 65)
    else:
        applicant_age = np_normal_int(45, 12, 25, 70)
    applicant_gender = random.choices(["Male", "Female", "Other"], [0.6, 0.38, 0.02])[0]
    if portfolio in ["CF", "PF"]:
        interest_rate = round(random.uniform(3.0, 5.0), 4)
    elif portfolio == "AF":
        interest_rate = round(random.uniform(2.5, 4.5), 4)
    elif portfolio == "MORTGAGE":
        interest_rate = round(random.uniform(1.2, 2.2), 4)
    else:
        interest_rate = round(random.uniform(2.0, 3.0), 4)
    margin = round(interest_rate * random.uniform(0.3, 0.7), 4)
    fee_amount = int(application_amount * random.uniform(0.01, 0.04))
    pre_approved_last_valid_date = (application_date + timedelta(days=random.randint(1, 30))) if main_channel == "Preapproved" else None
    currency = "TRY"
    salary_customer_flag = random.choices([True, False], [0.6, 0.4])[0] if portfolio in ["CF", "PF"] else random.choices([True, False], [0.2, 0.8])[0]
    existing_customer_flag = random.choices([True, False], [0.7, 0.3])[0]

    values = [
        report_date, report_country, report_portfolio, tx_id, application_date, main_channel, subchannels, purpose_of_loan,
        credit_bureau_null_flag, internal_model_score, expected_pd, policy_rules_flag, other_rule_flag, fraud_rule_flag, score_decline_flag,
        application_status, credit_bureau_query, credit_bureau_score, all_credit_bureau_raw_fields, other_credit_bureau_scores,
        rule_details, affordability_flag, net_income, net_expenditure, branch_id, branch_name, region_name, cash_collateral, time_with_bank,
        auto_decision_flag, application_tenor, application_amount, approved_date, approved_tenor, approved_amount, disbursed_date,
        disbursed_tenor, disbursed_amount, postponment_flag, postponment_month, equal_installment_flag, work_type, working_sector,
        decision_engine_name, credit_card_flag, credit_card_limit, overdraft_flag, overdraft_limit, car_loan_flag, car_loan_amount,
        mortgage_flag, mortgage_amount, model_drivers, rule_drivers, utm_source, manual_underwriter_id, affordability_reason,
        applicant_age, applicant_gender, interest_rate, margin, fee_amount, pre_approved_last_valid_date, currency,
        salary_customer_flag, existing_customer_flag
    ]
    row = tuple([clean_value(x) for x in values])
    rows.append(row)

columns = """
    report_date, report_country, report_portfolio, tx_id, application_date, main_channel, subchannels, purpose_of_loan,
    credit_bureau_null_flag, internal_model_score, expected_pd, policy_rules_flag, other_rule_flag, fraud_rule_flag, score_decline_flag,
    application_status, credit_bureau_query, credit_bureau_score, all_credit_bureau_raw_fields, other_credit_bureau_scores,
    rule_details, affordability_flag, net_income, net_expenditure, branch_id, branch_name, region_name, cash_collateral, time_with_bank,
    auto_decision_flag, application_tenor, application_amount, approved_date, approved_tenor, approved_amount, disbursed_date,
    disbursed_tenor, disbursed_amount, postponment_flag, postponment_month, equal_installment_flag, work_type, working_sector,
    decision_engine_name, credit_card_flag, credit_card_limit, overdraft_flag, overdraft_limit, car_loan_flag, car_loan_amount,
    mortgage_flag, mortgage_amount, model_drivers, rule_drivers, utm_source, manual_underwriter_id, affordability_reason,
    applicant_age, applicant_gender, interest_rate, margin, fee_amount, pre_approved_last_valid_date, currency,
    salary_customer_flag, existing_customer_flag
""".replace("\n", " ").replace("  ", " ").strip()

sql = f"INSERT INTO credit_application ({columns}) VALUES ({', '.join(['%s'] * len(rows[0]))})"
cur.executemany(sql, rows)
conn.commit()

print(f"{N} kayıt başarıyla eklendi!")
cur.close()
conn.close()
