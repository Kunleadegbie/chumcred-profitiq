import pandas as pd
from modules.calculations import safe_numeric


def revenue_summary(df, date_col, amount_col):
    data = df.copy()
    data[amount_col] = safe_numeric(data[amount_col])
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data = data.dropna(subset=[date_col])
    data["Month"] = data[date_col].dt.to_period("M").astype(str)

    total_revenue = data[amount_col].sum()
    transaction_count = len(data)
    average_transaction_value = (
        total_revenue / transaction_count if transaction_count > 0 else 0
    )
    average_monthly_revenue = data.groupby("Month")[amount_col].sum().mean()

    return {
        "total_revenue": total_revenue,
        "transaction_count": transaction_count,
        "average_transaction_value": average_transaction_value,
        "average_monthly_revenue": average_monthly_revenue,
        "data": data,
    }


def revenue_by_dimension(df, dimension_col, amount_col):
    data = df.copy()
    data[amount_col] = safe_numeric(data[amount_col])

    return (
        data.groupby(dimension_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )


def build_revenue_opportunity_map(
    monthly_revenue,
    amount_col,
    product_revenue=None,
    branch_revenue=None,
    customer_revenue=None,
):
    opportunities = []

    if len(monthly_revenue) >= 2:
        latest = monthly_revenue.iloc[-1][amount_col]
        previous = monthly_revenue.iloc[-2][amount_col]

        if latest < previous:
            opportunities.append(
                {
                    "Opportunity Area": "Recover Recent Revenue Decline",
                    "Observation": "Latest month revenue is below previous month.",
                    "Estimated Revenue Opportunity": previous - latest,
                    "Recommended Action": "Review products, branches, and customers responsible for the decline.",
                    "Priority": "High",
                }
            )

    if product_revenue is not None and not product_revenue.empty:
        avg_product = product_revenue[amount_col].mean()
        weak_products = product_revenue[product_revenue[amount_col] < avg_product]

        if not weak_products.empty:
            opportunities.append(
                {
                    "Opportunity Area": "Improve Weak Product Performance",
                    "Observation": f"{len(weak_products)} products/services are below average revenue contribution.",
                    "Estimated Revenue Opportunity": avg_product * len(weak_products) * 0.20,
                    "Recommended Action": "Review pricing, sales effort, visibility, bundling, and customer demand.",
                    "Priority": "Medium",
                }
            )

    if branch_revenue is not None and not branch_revenue.empty:
        avg_branch = branch_revenue[amount_col].mean()
        weak_branches = branch_revenue[branch_revenue[amount_col] < avg_branch]

        if not weak_branches.empty:
            opportunities.append(
                {
                    "Opportunity Area": "Improve Underperforming Branches",
                    "Observation": f"{len(weak_branches)} branches are below average revenue contribution.",
                    "Estimated Revenue Opportunity": avg_branch * len(weak_branches) * 0.15,
                    "Recommended Action": "Review branch leadership, sales discipline, location potential, and local market activity.",
                    "Priority": "High",
                }
            )

    if customer_revenue is not None and len(customer_revenue) >= 5:
        bottom_customers = customer_revenue.tail(5)
        opportunities.append(
            {
                "Opportunity Area": "Increase Revenue from Low-Value Customers",
                "Observation": "Several customers have low revenue contribution.",
                "Estimated Revenue Opportunity": bottom_customers[amount_col].mean() * 5 * 0.25,
                "Recommended Action": "Create cross-selling, upselling, reactivation, and account management actions.",
                "Priority": "Medium",
            }
        )

    if not opportunities:
        opportunities.append(
            {
                "Opportunity Area": "Revenue Growth Review Required",
                "Observation": "No major automated revenue gap detected.",
                "Estimated Revenue Opportunity": 0,
                "Recommended Action": "Conduct deeper review by product, customer, pricing, market, and branch performance.",
                "Priority": "Review",
            }
        )

    return pd.DataFrame(opportunities)