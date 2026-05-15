import pandas as pd


# ==========================================================
# SAMPLE INDUSTRY BENCHMARKS
# MVP STATIC BENCHMARKS
# ==========================================================
INDUSTRY_BENCHMARKS = {
    "Retail": {
        "cost_to_revenue_ratio": 65,
        "payroll_to_revenue_ratio": 15,
        "profit_margin": 12,
    },
    "Manufacturing": {
        "cost_to_revenue_ratio": 72,
        "payroll_to_revenue_ratio": 18,
        "profit_margin": 10,
    },
    "Banking": {
        "cost_to_revenue_ratio": 55,
        "payroll_to_revenue_ratio": 20,
        "profit_margin": 25,
    },
    "Telecommunications": {
        "cost_to_revenue_ratio": 60,
        "payroll_to_revenue_ratio": 12,
        "profit_margin": 28,
    },
    "Healthcare": {
        "cost_to_revenue_ratio": 70,
        "payroll_to_revenue_ratio": 22,
        "profit_margin": 15,
    },
    "Logistics": {
        "cost_to_revenue_ratio": 75,
        "payroll_to_revenue_ratio": 17,
        "profit_margin": 8,
    },
    "Technology": {
        "cost_to_revenue_ratio": 58,
        "payroll_to_revenue_ratio": 25,
        "profit_margin": 22,
    },
    "Education": {
        "cost_to_revenue_ratio": 68,
        "payroll_to_revenue_ratio": 30,
        "profit_margin": 10,
    },
    "Oil & Gas": {
        "cost_to_revenue_ratio": 62,
        "payroll_to_revenue_ratio": 14,
        "profit_margin": 30,
    },
    "General": {
        "cost_to_revenue_ratio": 65,
        "payroll_to_revenue_ratio": 20,
        "profit_margin": 15,
    },
}


# ==========================================================
# HELPER
# ==========================================================
def safe_number(value):
    try:
        return float(value)
    except Exception:
        return 0


# ==========================================================
# GET BENCHMARKS
# ==========================================================
def get_industry_benchmark(industry):
    if not industry:
        return INDUSTRY_BENCHMARKS["General"]

    return INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["General"])


# ==========================================================
# GENERATE BENCHMARK TABLE
# ==========================================================
def generate_benchmark_comparison(
    industry="General",
    total_revenue=0,
    total_cost=0,
    total_payroll=0,
    net_profit=0,
):
    benchmark = get_industry_benchmark(industry)

    total_revenue = safe_number(total_revenue)
    total_cost = safe_number(total_cost)
    total_payroll = safe_number(total_payroll)
    net_profit = safe_number(net_profit)

    # ======================================================
    # COMPANY KPIs
    # ======================================================
    cost_to_revenue = (
        (total_cost / total_revenue) * 100
        if total_revenue > 0
        else 0
    )

    payroll_to_revenue = (
        (total_payroll / total_revenue) * 100
        if total_revenue > 0
        else 0
    )

    profit_margin = (
        (net_profit / total_revenue) * 100
        if total_revenue > 0
        else 0
    )

    # ======================================================
    # BUILD COMPARISON
    # ======================================================
    comparison_df = pd.DataFrame(
        [
            {
                "KPI": "Cost-to-Revenue Ratio",
                "Company": round(cost_to_revenue, 1),
                "Industry Benchmark": benchmark["cost_to_revenue_ratio"],
                "Variance": round(
                    cost_to_revenue - benchmark["cost_to_revenue_ratio"],
                    1,
                ),
                "Performance": (
                    "Above Benchmark"
                    if cost_to_revenue > benchmark["cost_to_revenue_ratio"]
                    else "Within Benchmark"
                ),
            },
            {
                "KPI": "Payroll-to-Revenue Ratio",
                "Company": round(payroll_to_revenue, 1),
                "Industry Benchmark": benchmark["payroll_to_revenue_ratio"],
                "Variance": round(
                    payroll_to_revenue - benchmark["payroll_to_revenue_ratio"],
                    1,
                ),
                "Performance": (
                    "Above Benchmark"
                    if payroll_to_revenue > benchmark["payroll_to_revenue_ratio"]
                    else "Within Benchmark"
                ),
            },
            {
                "KPI": "Profit Margin",
                "Company": round(profit_margin, 1),
                "Industry Benchmark": benchmark["profit_margin"],
                "Variance": round(
                    profit_margin - benchmark["profit_margin"],
                    1,
                ),
                "Performance": (
                    "Above Benchmark"
                    if profit_margin > benchmark["profit_margin"]
                    else "Below Benchmark"
                ),
            },
        ]
    )

    return comparison_df


# ==========================================================
# GENERATE BENCHMARK INSIGHTS
# ==========================================================
def generate_benchmark_insights(comparison_df):
    insights = []

    if comparison_df is None or comparison_df.empty:
        return [
            "Benchmark comparison could not be generated due to insufficient data."
        ]

    for _, row in comparison_df.iterrows():
        kpi = row["KPI"]
        company = row["Company"]
        benchmark = row["Industry Benchmark"]
        variance = row["Variance"]

        if kpi == "Profit Margin":
            if company < benchmark:
                insights.append(
                    f"Profit margin is {abs(variance):.1f}% below industry benchmark."
                )
            else:
                insights.append(
                    f"Profit margin is {variance:.1f}% above industry benchmark."
                )

        else:
            if company > benchmark:
                insights.append(
                    f"{kpi} is {variance:.1f}% above industry benchmark and may require management attention."
                )
            else:
                insights.append(
                    f"{kpi} is within acceptable industry benchmark range."
                )

    insights.append(
        "Benchmarking should be interpreted alongside business strategy, market conditions, operating model, and growth stage."
    )

    return insights