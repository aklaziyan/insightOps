import random
import datetime

# --- Fonksiyonlar ---
def random_date(start, end):
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

def generate_branch(region_branches):
    region, branch_id = random.choice(region_branches)
    return branch_id, region

# --- Parametreler ---
regions = [
    ('Marmara-1', 12), ('Marmara-2', 12), ('Marmara-3', 12),
    ('Ege-1', 8), ('Ege-2', 8),
    ('Karadeniz-1', 7), ('Karadeniz-2', 7),
    ('Akdeniz', 10),
    ('İç Anadolu', 10),
    ('Doğu Anadolu', 8),
    ('Güneydoğu Anadolu', 6)
]
branch_names = ['Downtown','Shopping Mall','University','Airport','Neighborhood',
    'Android App','iOS App',
    'Personal Banking','Business Banking','Campaign Landing Page',
    'Inbound','Outbound','VIP Line','Support',
    'Electronics','Furniture','Clothing','Supermarket','Jewelry'
]
main_channels = [
    ('Branch',['Downtown','Shopping Mall','University','Airport','Neighborhood']),
    ('Mobile',['Android App','iOS App']),
    ('Web',['Personal Banking','Business Banking','Campaign Landing Page']),
    ('Call Center',['Inbound','Outbound','VIP Line','Support']),
    ('POS',['Electronics','Furniture','Clothing','Supermarket','Jewelry'])
]
purposes = [
    'Home Renovation','Car Purchase','Education','Holiday','Health Expenses',
    'Consumer Goods','Debt Consolidation','Wedding','Electronics','Furniture'
]
statuses = (['Rejected']*15 + ['In Process']*20 + ['Accepted']*50 + ['Disbursed']*15)
statuses = statuses* (3000 // 100) + random.choices(statuses, k=3000-len(statuses)*(3000//100))
country = 'Turkey'
portfolio = 'Consumer Finance'

# --- Branch dağılımı ---
region_branch_ids = []
branch_idx = 1
for region, branch_count in regions:
    for i in range(branch_count):
        region_branch_ids.append( (region, f'BRANCH{branch_idx:03}') )
        branch_idx += 1

# --- Tarih aralığı ---
today = datetime.date.today()
start_date = today - datetime.timedelta(days=730)
end_date = today

# --- Gelir segmentleri ---
def income_segment():
    rnd = random.random()
    if rnd < 0.25:
        return random.randint(25000,50000)
    elif rnd < 0.55:
        return random.randint(50000,100000)
    elif rnd < 0.85:
        return random.randint(100000,200000)
    else:
        return random.randint(200000,350000)

# --- Kredi skoru ve PD ---
def score_and_pd():
    r = random.random()
    if r < 0.10:
        score = random.randint(300,499)
        pd = round(random.uniform(0.12,0.25),3)
    elif r < 0.45:
        score = random.randint(500,699)
        pd = round(random.uniform(0.08,0.12),3)
    elif r < 0.80:
        score = random.randint(700,849)
        pd = round(random.uniform(0.02,0.08),3)
    else:
        score = random.randint(850,950)
        pd = round(random.uniform(0.005,0.019),3)
    return score, pd

# --- INSERT script üretimi ---
with open("insert_credit_applications.sql","w", encoding="utf-8") as f:
    for i in range(1,3001):
        # Tarihler
        app_date = random_date(start_date,end_date)
        report_date = app_date + datetime.timedelta(days=random.randint(0,2))
        t_start = app_date - datetime.timedelta(days=random.randint(90,5500))
        time_with_bank = t_start
        # Kanal ve subchannel
        main_channel, subchannels = random.choice(main_channels)
        subchannel = random.choice(subchannels)
        # Region ve branch
        branch_id, region = random.choice(region_branch_ids)
        branch_name = subchannel
        # Purpose
        purpose = random.choice(purposes)
        # Status
        application_status = random.choice(['Rejected','In Process','Accepted','Disbursed'])
        # TX ID
        tx_id = f"TX{i+10000:07}"
        # Credit Bureau Null Flag
        credit_bureau_null_flag = 1 if random.random() < 0.08 else 0
        # Skor ve PD
        internal_model_score, expected_pd = score_and_pd()
        # Credit Bureau Score
        credit_bureau_score = internal_model_score + random.randint(-10,10)
        # Flags
        policy_rules_flag = 1 if random.random()<0.18 else 0
        other_rule_flag = 1 if random.random()<0.12 else 0
        fraud_rule_flag = 1 if random.random()<0.08 else 0
        score_decline_flag = 1 if (internal_model_score < 600) else 0
        credit_bureau_query = 0 if random.random()<0.95 else -99
        rule_details_id = 'NULL'
        credit_bureau_response_id = 'NULL'
        other_credit_bureau_scores = 'NULL'
        affordability_flag = 1 if (income_segment()<35000 or expected_pd>0.18) else 0
        # Net income, expenditure
        net_income = income_segment()
        net_expenditure = int(net_income * random.uniform(0.15,0.65))
        # Collateral
        cash_collateral = random.randint(10000,200000) if random.random()<0.10 else 0
        # Auto Decision Flag
        auto_decision_flag = 1 if (internal_model_score>750 and expected_pd<0.03 and random.random()<0.8) else (1 if random.random()<0.20 else 0)
        # Status
        application_status = (
            "Rejected" if (internal_model_score < 600 and expected_pd > 0.10) else
            "Disbursed" if (internal_model_score > 800 and expected_pd < 0.015 and random.random()<0.65) else
            application_status
        )
        # SQL yaz
        f.write("INSERT INTO credit_applications (report_date, report_country, report_portfolio, tx_id, application_date, main_channel, subchannels, purpose_of_loan, credit_bureau_null_flag, internal_model_score, expected_pd, policy_rules_flag, other_rule_flag, fraud_rule_flag, score_decline_flag, application_status, credit_bureau_query, credit_bureau_score, credit_bureau_response_id, other_credit_bureau_scores, rule_details_id, affordability_flag, net_income, net_expenditure, branch_id, branch_name, region_name, cash_collateral, time_with_bank, auto_decision_flag, created_at, updated_at) VALUES\n")
        f.write(f"('{report_date}','{country}','{portfolio}','{tx_id}','{app_date}','{main_channel}','{subchannel}','{purpose}',{credit_bureau_null_flag},{internal_model_score},{expected_pd},{policy_rules_flag},{other_rule_flag},{fraud_rule_flag},{score_decline_flag},'{application_status}',{credit_bureau_query},{credit_bureau_score},{credit_bureau_response_id},{other_credit_bureau_scores},{rule_details_id},{affordability_flag},{net_income},{net_expenditure},'{branch_id}','{branch_name}','{region}',{cash_collateral},'{time_with_bank}',{auto_decision_flag},NOW(),NOW());\n\n")
