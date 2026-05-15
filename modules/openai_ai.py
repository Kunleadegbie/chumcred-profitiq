import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ==========================================================
# OPENAI CLIENT SETUP
# ==========================================================
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def get_ai_model():
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


# ==========================================================
# DATA HELPERS
# ==========================================================
def dataframe_sample(df, max_rows=20):
    if df is None:
        return "No data available."

    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df)
        except Exception:
            return "Invalid data format."

    if df.empty:
        return "No data available."

    sample = df.head(max_rows).copy()
    return sample.to_json(orient="records", indent=2, default_handler=str)


def safe_json(data):
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception:
        return str(data)


# ==========================================================
# BASE OPENAI CALL
# ==========================================================
def ask_openai(system_prompt, user_prompt, temperature=0.3):
    client = get_openai_client()

    if client is None:
        return "OpenAI API key not found. Please add OPENAI_API_KEY to your .env file."

    try:
        response = client.chat.completions.create(
            model=get_ai_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis failed: {e}"


# ==========================================================
# GENERAL EXECUTIVE COMMENTARY
# ==========================================================
def generate_ai_executive_commentary(
    company_name,
    revenue_opportunity_df=None,
    leakage_df=None,
    cost_saving_df=None,
    action_plan_df=None,
):
    system_prompt = """
You are a senior business transformation consultant.
Write clear, executive-level analysis in simple business English.
Focus on revenue growth, leakage reduction, cost savings, risks, and practical next steps.
Avoid exaggeration. Be professional and concise.
"""

    user_prompt = f"""
Company: {company_name}

Revenue Opportunity Data:
{dataframe_sample(revenue_opportunity_df)}

Leakage Data:
{dataframe_sample(leakage_df)}

Cost Saving Data:
{dataframe_sample(cost_saving_df)}

Action Plan Data:
{dataframe_sample(action_plan_df)}

Prepare an executive commentary covering:
1. Overall business situation
2. Major revenue opportunities
3. Leakage risks
4. Cost-saving opportunities
5. Recommended management priorities
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# CONSULTING RECOMMENDATIONS
# ==========================================================
def generate_ai_consulting_recommendations(
    company_name,
    revenue_opportunity_df=None,
    leakage_df=None,
    cost_saving_df=None,
):
    system_prompt = """
You are a practical management consultant.
Generate actionable recommendations that a CEO, CFO, or management team can implement within 90 days.
Use professional consulting language but keep it simple and practical.
"""

    user_prompt = f"""
Company: {company_name}

Revenue Opportunities:
{dataframe_sample(revenue_opportunity_df)}

Leakage Register:
{dataframe_sample(leakage_df)}

Cost Savings Report:
{dataframe_sample(cost_saving_df)}

Generate:
1. Quick wins
2. Medium-term actions
3. Control improvements
4. Revenue growth actions
5. Cost reduction actions
6. Management priorities for the next 90 days
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# DIAGNOSTIC SUMMARY
# ==========================================================
def generate_ai_diagnostic_summary(
    company_name,
    diagnostic_df=None,
    benchmark_df=None,
    forecast_df=None,
):
    system_prompt = """
You are an executive business analyst.
Summarize diagnostic findings clearly for management decision-making.
Focus on business performance, operational risks, revenue growth, cost control, and profitability.
"""

    user_prompt = f"""
Company: {company_name}

Business Diagnostic:
{dataframe_sample(diagnostic_df)}

Benchmarking:
{dataframe_sample(benchmark_df)}

Forecast:
{dataframe_sample(forecast_df)}

Write a diagnostic summary highlighting:
1. Strengths
2. Weaknesses
3. Risks
4. Improvement areas
5. Management actions required
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# REVENUE ANALYSIS INSIGHT
# ==========================================================
def generate_ai_revenue_analysis(
    company_name,
    revenue_summary=None,
    monthly_revenue_df=None,
    product_revenue_df=None,
    branch_revenue_df=None,
    customer_revenue_df=None,
    revenue_opportunity_df=None,
):
    system_prompt = """
You are a senior revenue growth consultant.
Interpret revenue data professionally for management.
Focus on revenue growth, underperformance, customer/product/branch opportunities, and practical commercial actions.
"""

    user_prompt = f"""
Company: {company_name}

Revenue Summary:
{safe_json(revenue_summary)}

Monthly Revenue:
{dataframe_sample(monthly_revenue_df)}

Product Revenue:
{dataframe_sample(product_revenue_df)}

Branch Revenue:
{dataframe_sample(branch_revenue_df)}

Customer Revenue:
{dataframe_sample(customer_revenue_df)}

Revenue Opportunity Map:
{dataframe_sample(revenue_opportunity_df)}

Write a professional revenue analysis insight covering:
1. Revenue performance
2. Growth opportunities
3. Weak areas
4. Possible causes
5. Recommended management actions
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# LEAKAGE REVIEW INSIGHT
# ==========================================================
def generate_ai_leakage_review(
    company_name,
    leakage_df=None,
    total_leakage_exposure=0,
):
    system_prompt = """
You are a revenue assurance and internal control consultant.
Interpret leakage findings professionally.
Focus on leakage exposure, control weaknesses, validation steps, recovery opportunities, and management action.
"""

    user_prompt = f"""
Company: {company_name}

Total Leakage Exposure:
{total_leakage_exposure}

Leakage Register:
{dataframe_sample(leakage_df)}

Write a professional leakage review insight covering:
1. Key leakage risks
2. Possible root causes
3. Control weaknesses
4. Financial exposure
5. Immediate validation and recovery steps
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# COST REVIEW INSIGHT
# ==========================================================
def generate_ai_cost_review(
    company_name,
    cost_summary=None,
    cost_saving_df=None,
    expense_df=None,
    payroll_df=None,
    vendor_df=None,
):
    system_prompt = """
You are a cost optimization and operational efficiency consultant.
Interpret cost data professionally for management.
Focus on cost pressure, avoidable expenses, vendor concentration, payroll efficiency, and savings opportunities.
"""

    user_prompt = f"""
Company: {company_name}

Cost Summary:
{safe_json(cost_summary)}

Cost Savings Report:
{dataframe_sample(cost_saving_df)}

Expense Data Sample:
{dataframe_sample(expense_df)}

Payroll Data Sample:
{dataframe_sample(payroll_df)}

Vendor Data Sample:
{dataframe_sample(vendor_df)}

Write a professional cost review insight covering:
1. Cost structure
2. Cost pressure areas
3. Possible avoidable costs
4. Vendor/payroll concerns
5. Practical savings opportunities
6. Management actions for the next 90 days
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# DASHBOARD EXECUTIVE SUMMARY
# ==========================================================
def generate_ai_dashboard_summary(
    company_name,
    dashboard_summary=None,
    priority_action_df=None,
    benchmark_df=None,
    risk_heatmap_df=None,
    forecast_df=None,
):
    system_prompt = """
You are a board-level executive intelligence analyst.
Write concise management commentary from dashboard outputs.
Focus on what the CEO, CFO, and board should understand and act on.
"""

    user_prompt = f"""
Company: {company_name}

Dashboard Summary:
{safe_json(dashboard_summary)}

Priority Actions:
{dataframe_sample(priority_action_df)}

Benchmarking:
{dataframe_sample(benchmark_df)}

Risk Heatmap:
{dataframe_sample(risk_heatmap_df)}

Forecast:
{dataframe_sample(forecast_df)}

Write a board-level dashboard summary covering:
1. Overall business position
2. Biggest value drivers
3. Main risks
4. Priority actions
5. 90-day executive focus
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# BOARD REPORT NARRATIVE
# ==========================================================
def generate_ai_board_report(
    company_name,
    executive_summary=None,
    diagnostic_df=None,
    revenue_opportunity_df=None,
    leakage_df=None,
    cost_saving_df=None,
    action_plan_df=None,
    benchmark_df=None,
    forecast_df=None,
):
    system_prompt = """
You are a board report writer and senior management consultant.
Write in a professional, concise, board-ready style.
Avoid technical jargon. Focus on value, risk, action, and management accountability.
"""

    user_prompt = f"""
Company: {company_name}

Executive Summary:
{safe_json(executive_summary)}

Diagnostic Report:
{dataframe_sample(diagnostic_df)}

Revenue Opportunity Map:
{dataframe_sample(revenue_opportunity_df)}

Leakage Register:
{dataframe_sample(leakage_df)}

Cost Savings Report:
{dataframe_sample(cost_saving_df)}

Action Plan:
{dataframe_sample(action_plan_df)}

Benchmarking:
{dataframe_sample(benchmark_df)}

Forecast:
{dataframe_sample(forecast_df)}

Prepare a board-level narrative report covering:
1. Executive overview
2. Key findings
3. Financial implications
4. Risk implications
5. Recommended management actions
6. 90-day implementation priorities
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# ACTION PLAN RECOMMENDATION
# ==========================================================
def generate_ai_action_plan(
    company_name,
    priority_action_df=None,
    leakage_df=None,
    cost_saving_df=None,
    revenue_opportunity_df=None,
):
    system_prompt = """
You are a practical implementation consultant.
Convert findings into a focused 90-day execution plan.
Recommendations must be clear, actionable, and management-friendly.
"""

    user_prompt = f"""
Company: {company_name}

Priority Actions:
{dataframe_sample(priority_action_df)}

Revenue Opportunities:
{dataframe_sample(revenue_opportunity_df)}

Leakage Findings:
{dataframe_sample(leakage_df)}

Cost Savings:
{dataframe_sample(cost_saving_df)}

Create a 90-day execution plan covering:
1. Quick wins
2. High-priority actions
3. Responsible departments
4. Expected outcomes
5. Weekly tracking discipline
6. Management escalation areas
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# FORECAST COMMENTARY
# ==========================================================
def generate_ai_forecast_commentary(
    company_name,
    revenue_forecast_df=None,
    cost_forecast_df=None,
    profit_forecast_df=None,
):
    system_prompt = """
You are a financial planning and performance analyst.
Interpret forecast outputs in simple executive language.
Focus on expected performance, risks, pressure points, and management actions.
"""

    user_prompt = f"""
Company: {company_name}

Revenue Forecast:
{dataframe_sample(revenue_forecast_df)}

Cost Forecast:
{dataframe_sample(cost_forecast_df)}

Profit Forecast:
{dataframe_sample(profit_forecast_df)}

Write forecast commentary covering:
1. Expected revenue movement
2. Expected cost movement
3. Profit outlook
4. Risk areas
5. Management actions required
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# BENCHMARK COMMENTARY
# ==========================================================
def generate_ai_benchmark_commentary(
    company_name,
    benchmark_df=None,
):
    system_prompt = """
You are an industry benchmarking consultant.
Explain benchmark performance clearly for executive decision-making.
"""

    user_prompt = f"""
Company: {company_name}

Benchmark Comparison:
{dataframe_sample(benchmark_df)}

Write benchmarking commentary covering:
1. Where the company is performing well
2. Where it is below benchmark
3. What the variance means
4. What management should do next
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# HEATMAP COMMENTARY
# ==========================================================
def generate_ai_heatmap_commentary(
    company_name,
    branch_risk_heatmap_df=None,
    cost_concentration_heatmap_df=None,
    leakage_risk_matrix_df=None,
    profitability_heatmap_df=None,
):
    system_prompt = """
You are an executive risk and performance analyst.
Interpret heatmaps for management action.
Focus on branch risk, cost concentration, leakage risk, and profitability concentration.
"""

    user_prompt = f"""
Company: {company_name}

Branch Risk Heatmap:
{dataframe_sample(branch_risk_heatmap_df)}

Cost Concentration Heatmap:
{dataframe_sample(cost_concentration_heatmap_df)}

Leakage Risk Matrix:
{dataframe_sample(leakage_risk_matrix_df)}

Profitability Heatmap:
{dataframe_sample(profitability_heatmap_df)}

Write heatmap commentary covering:
1. Main risk clusters
2. Concentration risks
3. Branch/product concerns
4. Management priorities
5. Recommended actions
"""

    return ask_openai(system_prompt, user_prompt)


# ==========================================================
# AI ASSISTANT QUESTION ANSWERING
# ==========================================================
def answer_business_question(question, context_data):
    system_prompt = """
You are Chumcred ProfitIQ AI Assistant.
Answer questions strictly based on the business data provided.
If the data is insufficient, say what data is missing.
Be clear, practical, and executive-friendly.
Do not expose raw JSON unless specifically requested.
"""

    user_prompt = f"""
Business Data Context:
{safe_json(context_data)}

User Question:
{question}
"""

    return ask_openai(system_prompt, user_prompt)