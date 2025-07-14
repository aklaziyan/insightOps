import psycopg2
from faker import Faker
import random
import numpy as np
from datetime import datetime, timedelta

# --- PostgreSQL bağlantı ayarlarını doldur ---
DB_NAME = "insightops"
DB_USER = "cihan"
DB_PASS = "insightops"   # şifreyi değiştir
DB_HOST = "localhost"
DB_PORT = 5432

# --- Kayıt sayısı ---
N = 10000

fake = Faker()
random.seed(42)
np.random.seed(42)

# --- Portföy dağılımı ---
portfolio_choices = (["CF"] * 4500 + ["PF"] * 2500 + ["AF"] * 2000 + ["CORP"] * 300 + ["MORTGAGE"] * 700)
random.shuffle(portfolio_choices)

# --- Main channel ve subchannel kuralları ---
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

def normal_value(low, high, avg, stddev, minv=None, maxv=None):
    """Normal dağılımda, limitlere dikkat ederek random float üretir."""
    val = int(np.clip(np.random.normal(avg, stddev), low, high))
    if minv is not None and val < minv:
        val = minv
    if maxv is not None and val > maxv:
        val = maxv
    return val

# Bağlantı kur
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()

today = datetime.now()

for i in range(N):
    # --- Rapor tarihi ve ülke ---
    report_date = today.strftime("%Y-%m-%d %H:%M:%S")
    report_country = "Turkey"

    # --- Portfolio ---
    portfolio = portfolio_choices[i]

    # --- Portföyden diğer alanların varsayılanlarını üret ---
    # --- tx_id ve application_date ---
    tx_id = f"TX{str(i+1).zfill(7)}"
    application_date = today - timedelta(days=random.randint(0, 730), hours=random.randint(0, 23), minutes=random.randint(0, 59))

    # --- Main channel & subchannels ---
    main_channel = random.choice(main_channel_map[portfolio])
    if main_channel in subchannels_map:
        subchannels = random.choice(subchannels_map[main_channel])
    else:
        subchannels = None

    # --- Purpose of loan ---
    purpose_of_loan = random.choice(purpose_map[portfolio])

    # --- Credit bureau null flag ---
    credit_bureau_null_flag = random.choices([False, True], [0.95, 0.05])[0]

    # --- Internal model score (400-1000) ve PD (0.01-0.3 ters orantı) ---
    internal_model_score = round(random.uniform(400, 1000), 4)
    expected_pd = round(np.clip((1.1 - (internal_model_score / 1000)) * random.uniform(0.01, 0.3), 0.01, 0.3), 4)

    # --- Policy/Other/Fraud flags ---
    policy_rules_flag = random.choices([False, True], [0.97, 0.03])[0]
    other_rule_flag = random.choices([False, True], [0.95, 0.05])[0]
    fraud_rule_flag = random.choices([False, True], [0.99, 0.01])[0]

    # --- Statü mantığı için gün ve portföy ---
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

    # --- Score decline flag (sadece Rejected olanlarda %90 1, diğerlerinde 0) ---
    if application_status == "Rejected":
        score_decline_flag = 1 if random.random() < 0.9 else 0
    else:
        score_decline_flag = 0

    # --- Credit bureau query, score, other score ---
    credit_bureau_query = random.choices(["0", "-99", "1"], [0.97, 0.02, 0.01])[0]
    credit_bureau_score = (round(random.uniform(300, 1900), 4) if credit_bureau_query != "-99" else None)
    all_credit_bureau_raw_fields = 1000 + i  # 1000–3999 arası unique id
    other_credit_bureau_scores = (round(random.uniform(300, 1900), 4) if random.random() < 0.2 else None)

    # --- Rule details ---
    if random.random() < 0.3:
        rule_details = ";".join(random.sample(rule_code_options, k=random.randint(1, 3)))
    else:
        rule_details = None

    # --- Affordability flag/reason ---
    affordability_flag = random.choices([False, True], [0.90, 0.10])[0]
    net_income = None
    if portfolio in ["CF", "PF"]:
        net_income = round(np.random.normal(250000, 60000), 2)
        net_income = int(np.clip(net_income, 25000, 250000))
    elif portfolio == "MORTGAGE":
        net_income = round(np.random.normal(350000, 100000), 2)
        net_income = int(np.clip(net_income, 100000, 1000000))
    elif portfolio == "CORP":
        net_income = round(np.random.normal(10000000, 6000000), 2)
        net_income = int(np.clip(net_income, 1000000, 100000000))
    else:
        net_income = round(np.random.normal(1500000, 350000), 2)
        net_income = int(np.clip(net_income, 500000, 7500000))
    # Net expenditure: gelirin %30-90 arası, %10 NULL
    net_expenditure = (str(int(net_income * random.uniform(0.3, 0.9))) if random.random() > 0.1 else None)

    # --- Branch & Region (sadece branch kanalında) ---
    if main_channel == "Branch":
        branch_id = random.choice(branch_ids)
        branch_name = branch_id
        region_name = branch_region_map[branch_id]
    else:
        branch_id = branch_name = region_name = None

    # --- Cash collateral (disbursed/accepted ve Mortgage/Auto/Corp %10 dolu) ---
    cash_collateral = None
    if application_status in ["Disbursed", "Accepted"] and portfolio in ["AF", "MORTGAGE", "CORP"] and random.random() < 0.1:
        cash_collateral = str(int(np.random.normal(1500000, 500000)))

    # --- Time with bank (application_date’ten 1–15 yıl önce) ---
    years_with_bank = random.randint(0, 15)
    time_with_bank = application_date - timedelta(days=years_with_bank * 365)

    # --- Auto decision flag ---
    if portfolio in ["CF", "PF", "AF"]:
        auto_decision_flag = random.choices([True, False], [0.8, 0.2])[0]
    else:
        auto_decision_flag = random.choices([True, False], [0.2, 0.8])[0]

    # --- Application tenor ---
    if portfolio in ["CF", "PF"]:
        tenors = ["12"] * 50 + ["24"] * 30 + ["36"] * 15 + ["48"] * 5
        application_tenor = random.choice(tenors)
    elif portfolio == "MORTGAGE":
        tenors = ["60"] * 35 + ["84"] * 35 + ["120"] * 20 + ["180"] * 10
        application_tenor = random.choice(tenors)
    elif portfolio == "AF":
        tenors = ["24"] * 50 + ["36"] * 30 + ["48"] * 20
        application_tenor = random.choice(tenors)
    else:
        tenors = ["12", "24", "36", "48", "60"]
        application_tenor = random.choice(tenors)

    # --- Application amount ---
    if portfolio in ["CF", "PF"]:
        application_amount = int(np.clip(np.random.normal(250000, 75000), 50000, 1250000))
    elif portfolio == "AF":
        application_amount = int(np.clip(np.random.normal(2000000, 750000), 500000, 7500000))
    elif portfolio == "MORTGAGE":
        application_amount = int(np.clip(np.random.normal(5000000, 1500000), 1000000, 50000000))
    else:
        application_amount = int(np.clip(np.random.normal(10000000, 6000000), 2500000, 125000000))

    # --- Approved/disbursed alanlar ---
    if application_status in ["Accepted", "Disbursed"]:
        approved_date = application_date + timedelta(days=random.randint(1, 14))
        approved_tenor = application_tenor  # veya ±1 ay değişebilir
        approved_amount = int(application_amount * random.uniform(0.95, 1))
    else:
        approved_date = approved_tenor = approved_amount = None

    if application_status == "Disbursed":
        disbursed_date = approved_date + timedelta(days=random.randint(1, 10)) if approved_date else None
        disbursed_tenor = approved_tenor
        disbursed_amount = int(approved_amount * random.uniform(0.98, 1)) if approved_amount else None
    else:
        disbursed_date = disbursed_tenor = disbursed_amount = None

    # --- Postponment flag/month (disbursed ve Auto/Mortgage/Corp %10) ---
    postponment_flag = None
    postponment_month = None
    if application_status == "Disbursed" and portfolio in ["AF", "MORTGAGE", "CORP"] and random.random() < 0.1:
        postponment_flag = True
        postponment_month = (disbursed_date + timedelta(days=random.randint(0, 90))).strftime("%Y-%m")
    else:
        postponment_flag = False

    # --- Equal installment flag ---
    if portfolio in ["CF", "PF"]:
        equal_installment_flag = random.choices([True, False], [0.9, 0.1])[0]
    elif portfolio == "MORTGAGE":
        equal_installment_flag = random.choices([True, False], [0.7, 0.3])[0]
    elif portfolio == "AF":
        equal_installment_flag = random.choices([True, False], [0.7, 0.3])[0]
    else:
        equal_installment_flag = random.choices([True, False], [0.6, 0.4])[0]

    # --- Work type / working sector ---
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

    # --- Decision engine name ---
    decision_engine_name = random.choice(decision_engine_names)

    # --- credit_card_flag / limit ---
    credit_card_flag = random.choices([True, False], [0.6, 0.4])[0]
    credit_card_limit = int(random.uniform(50000, 750000)) if credit_card_flag else None

    # --- overdraft_flag / limit ---
    overdraft_flag = random.choices([True, False], [0.3, 0.7])[0]
    overdraft_limit = int(random.uniform(10000, 100000)) if overdraft_flag else None

    # --- car_loan_flag / amount ---
    if portfolio == "AF":
        car_loan_flag = random.choices([True, False], [0.6, 0.4])[0]
    elif portfolio in ["CF", "PF"]:
        car_loan_flag = random.choices([True, False], [0.05, 0.95])[0]
    else:
        car_loan_flag = random.choices([True, False], [0.02, 0.98])[0]
    car_loan_amount = int(random.uniform(500000, 7000000)) if car_loan_flag else None

    # --- mortgage_flag / amount ---
    if portfolio == "MORTGAGE":
        mortgage_flag = random.choices([True, False], [0.98, 0.02])[0]
    else:
        mortgage_flag = random.choices([True, False], [0.02, 0.98])[0]
    mortgage_amount = int(random.uniform(1000000, 50000000)) if mortgage_flag else None

    # --- Model/rule drivers ---
    model_drivers = round(random.uniform(0.5, 1.5), 4) if random.random() > 0.2 else None
    rule_drivers = round(random.uniform(0.5, 1.5), 4) if random.random() > 0.2 else None

    # --- UTM source (kanala göre mantıklı) ---
    if main_channel in ["Public Web", "Mobile"]:
        utm_source = random.choice(utm_options)
    elif main_channel == "POS":
        utm_source = None
    else:
        utm_source = random.choice(["GoogleAds", "Organic", "Referral", "Direct"])

    # --- manual_underwriter_id (manuel başvurularda) ---
    manual_underwriter_id = random.choice([f"UW{str(j+1).zfill(3)}" for j in range(10)]) if not auto_dec
