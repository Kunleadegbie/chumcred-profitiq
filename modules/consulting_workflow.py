import pandas as pd
from datetime import date, timedelta


def create_default_workflow():
    today = date.today()

    workflow = [
        {
            "Phase": "1. Client Onboarding",
            "Activity": "Confirm client details, review objectives, stakeholders, and data requirements.",
            "Owner": "",
            "Start Date": today,
            "Due Date": today + timedelta(days=3),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "2. Data Collection",
            "Activity": "Collect sales, expense, bank, payroll, vendor, inventory, and branch performance data.",
            "Owner": "",
            "Start Date": today + timedelta(days=1),
            "Due Date": today + timedelta(days=10),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "3. Business Diagnostic",
            "Activity": "Review company profile, business model, revenue streams, cost structure, and key challenges.",
            "Owner": "",
            "Start Date": today + timedelta(days=5),
            "Due Date": today + timedelta(days=15),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "4. Analysis & Findings",
            "Activity": "Run revenue analysis, leakage detection, cost review, benchmarking, heatmaps, and forecasting.",
            "Owner": "",
            "Start Date": today + timedelta(days=10),
            "Due Date": today + timedelta(days=35),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "5. Management Review",
            "Activity": "Present findings to management, validate assumptions, confirm priorities, and agree quick wins.",
            "Owner": "",
            "Start Date": today + timedelta(days=30),
            "Due Date": today + timedelta(days=45),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "6. 90-Day Execution",
            "Activity": "Track assigned actions, owners, timelines, expected impact, actual impact, and blockers.",
            "Owner": "",
            "Start Date": today + timedelta(days=45),
            "Due Date": today + timedelta(days=90),
            "Status": "Not Started",
            "Notes": "",
        },
        {
            "Phase": "7. Final Report & Closeout",
            "Activity": "Generate final executive report, impact summary, lessons learned, and next-step recommendations.",
            "Owner": "",
            "Start Date": today + timedelta(days=80),
            "Due Date": today + timedelta(days=90),
            "Status": "Not Started",
            "Notes": "",
        },
    ]

    return pd.DataFrame(workflow)


def generate_workflow_summary(workflow_df):
    if workflow_df is None or workflow_df.empty:
        return pd.DataFrame()

    summary = (
        workflow_df.groupby("Status", as_index=False)
        .agg(Activities=("Activity", "count"))
        .sort_values("Activities", ascending=False)
    )

    return summary


def generate_workflow_insights(workflow_df):
    insights = []

    if workflow_df is None or workflow_df.empty:
        return ["No consulting workflow has been created yet."]

    total = len(workflow_df)
    completed = len(workflow_df[workflow_df["Status"] == "Completed"])
    in_progress = len(workflow_df[workflow_df["Status"] == "In Progress"])
    delayed = len(workflow_df[workflow_df["Status"] == "Delayed"])

    completion_rate = (completed / total * 100) if total > 0 else 0

    insights.append(f"The consulting workflow contains {total} key activities.")
    insights.append(f"Current completion rate is {completion_rate:.1f}%.")

    if in_progress > 0:
        insights.append(f"{in_progress} activity/activities are currently in progress.")

    if delayed > 0:
        insights.append(f"{delayed} delayed activity/activities require management attention.")

    if completion_rate < 50:
        insights.append("The engagement is still in early execution stage and requires close follow-up.")
    else:
        insights.append("The engagement is progressing and should continue with disciplined weekly tracking.")

    return insights