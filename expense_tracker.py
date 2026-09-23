"""
Personal Expense Tracker with Visualization
--------------------------------------------
A simple command-line application to record, categorize, and analyze
personal expenses. Data is stored persistently in a local SQLite
database. Uses Pandas for aggregation and Matplotlib/Seaborn for
visualizing spending patterns.

Author: Elavarasan B
Tech stack: Python, SQLite, Pandas, Matplotlib, Seaborn
"""

import sqlite3
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_NAME = "expenses.db"


# ---------- Database setup ----------

def init_db():
    """Create the expenses table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- Core operations ----------

def add_expense(date, category, amount, note=""):
    """Insert a new expense record into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date, category, amount, note),
    )
    conn.commit()
    conn.close()
    print(f"Added: {date} | {category} | ₹{amount} | {note}")


def load_expenses_df():
    """Load all expenses from the database into a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def show_summary():
    """Print total spending and a category-wise breakdown."""
    df = load_expenses_df()
    if df.empty:
        print("No expenses recorded yet.")
        return

    total = df["amount"].sum()
    print(f"\nTotal spending: ₹{total:.2f}")

    print("\nCategory-wise spending:")
    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    print(category_totals.to_string())

    df["month"] = df["date"].dt.to_period("M")
    print("\nMonth-wise spending:")
    monthly_totals = df.groupby("month")["amount"].sum()
    print(monthly_totals.to_string())


def visualize_expenses():
    """Generate a bar chart (category-wise) and a line chart (monthly trend)."""
    df = load_expenses_df()
    if df.empty:
        print("No expenses recorded yet. Add some before visualizing.")
        return

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Category-wise bar chart
    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    sns.barplot(x=category_totals.values, y=category_totals.index, hue=category_totals.index,
                ax=axes[0], palette="Blues_d", legend=False)
    axes[0].set_title("Spending by Category")
    axes[0].set_xlabel("Amount (₹)")
    axes[0].set_ylabel("Category")

    # Monthly trend line chart
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_totals = df.groupby("month")["amount"].sum()
    axes[1].plot(monthly_totals.index, monthly_totals.values, marker="o", color="#2563EB")
    axes[1].set_title("Monthly Spending Trend")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Amount (₹)")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig("expense_report.png", dpi=150)
    print("Chart saved as expense_report.png")
    plt.show()


# ---------- Command-line menu ----------

def main():
    init_db()
    while True:
        print("\n--- Personal Expense Tracker ---")
        print("1. Add expense")
        print("2. View summary")
        print("3. Visualize spending")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            date = input("Date (YYYY-MM-DD) [leave blank for today]: ").strip()
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            category = input("Category (e.g. Food, Travel, Bills): ").strip()
            amount = float(input("Amount: ").strip())
            note = input("Note (optional): ").strip()
            add_expense(date, category, amount, note)

        elif choice == "2":
            show_summary()

        elif choice == "3":
            visualize_expenses()

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
