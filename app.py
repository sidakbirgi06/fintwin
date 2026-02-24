from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary storage for demo purposes
user_data = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        user_data["income"] = int(request.form["income"])
        user_data["expenses"] = int(request.form["expenses"])
        user_data["assets"] = int(request.form["assets"])
        user_data["liabilities"] = int(request.form["liabilities"])
        user_data["goal"] = int(request.form["goal"])

        return redirect(url_for("dashboard"))

    return render_template("setup.html")

@app.route("/dashboard")
def dashboard():
    if not user_data:
        return redirect(url_for("setup"))

    # ----------------------------
    # Base Financial Data
    # ----------------------------
    income = user_data["income"]
    expenses = user_data["expenses"]
    assets = user_data["assets"]
    liabilities = user_data["liabilities"]
    goal = user_data["goal"]

    monthly_surplus = income - expenses
    net_worth = assets - liabilities

    # ----------------------------
    # Goal Readiness Score
    # ----------------------------
    if net_worth >= goal:
        goal_score = 90
    elif net_worth >= goal * 0.5:
        goal_score = 60
    else:
        goal_score = 30

    # ----------------------------
    # Financial Health Score
    # ----------------------------
    savings_rate = monthly_surplus / income if income > 0 else 0

    if savings_rate >= 0.3:
        savings_score = 40
    elif savings_rate >= 0.15:
        savings_score = 25
    else:
        savings_score = 10

    if net_worth > 0:
        net_worth_score = 30
    else:
        net_worth_score = 10

    goal_component = goal_score * 0.3

    financial_health_score = int(
        savings_score + net_worth_score + goal_component
    )

    # ----------------------------
    # Time-Based Future Projection
    # ----------------------------
    projection_5y = net_worth + (monthly_surplus * 12 * 5)
    projection_10y = net_worth + (monthly_surplus * 12 * 10)
    projection_20y = net_worth + (monthly_surplus * 12 * 20)

    # ----------------------------
    # Render Dashboard
    # ----------------------------
    return render_template(
        "dashboard.html",
        income=income,
        expenses=expenses,
        monthly_surplus=monthly_surplus,
        net_worth=net_worth,
        goal_score=goal_score,
        financial_health_score=financial_health_score,
        projection_5y=projection_5y,
        projection_10y=projection_10y,
        projection_20y=projection_20y
    )



@app.route("/simulate", methods=["GET", "POST"])
def simulate():
    if not user_data:
        return redirect(url_for("setup"))

    if request.method == "POST":

        # ----------------------------
        # BASE FINANCIAL TWIN
        # ----------------------------
        income = user_data["income"]
        expenses = user_data["expenses"]
        assets = user_data["assets"]
        liabilities = user_data["liabilities"]
        goal = user_data["goal"]

        base_surplus = income - expenses
        base_net_worth = assets - liabilities

        if base_net_worth >= goal:
            base_goal_score = 90
        elif base_net_worth >= goal * 0.5:
            base_goal_score = 60
        else:
            base_goal_score = 30

        # ----------------------------
        # CHECK IF LIFE-EVENT SIMULATION
        # ----------------------------
        life_event = request.form.get("life_event")

        if life_event == "house":

            asset_type = request.form.get("asset_type")
            asset_price = int(request.form.get("asset_price"))
            down_payment = int(request.form.get("down_payment"))
            emi = int(request.form.get("emi"))

            # Affordability check
            if emi <= base_surplus * 0.5:
                affordability = "Comfortable"
            elif emi <= base_surplus:
                affordability = "Moderate Risk"
            else:
                affordability = "Not Affordable"

            # Time to save down payment
            savings_rate = base_surplus if base_surplus > 0 else 0
            years_to_save = (
                down_payment / (savings_rate * 12)
                if savings_rate > 0 else None
            )

            # Impact simulation
            sim_assets = assets - down_payment
            sim_liabilities = liabilities + (asset_price - down_payment)
            sim_net_worth = sim_assets - sim_liabilities

            if sim_net_worth >= goal:
                sim_goal_score = 90
            elif sim_net_worth >= goal * 0.5:
                sim_goal_score = 60
            else:
                sim_goal_score = 30

            return render_template(
                "life_event_result.html",
                asset_type=asset_type,
                asset_price=asset_price,
                down_payment=down_payment,
                emi=emi,
                affordability=affordability,
                years_to_save=round(years_to_save, 1) if years_to_save else "Not feasible",
                sim_net_worth=sim_net_worth,
                sim_goal_score=sim_goal_score
            )

        # ----------------------------
        # GENERIC WHAT-IF SIMULATION
        # ----------------------------
        investment_increase = int(request.form.get("investment_increase", 0))
        expense_increase = int(request.form.get("expense_increase", 0))
        income_change = int(request.form.get("income_change", 0))
        new_loan = int(request.form.get("new_loan", 0))

        sim_income = income + income_change
        sim_expenses = expenses + expense_increase + investment_increase
        sim_assets = assets + investment_increase
        sim_liabilities = liabilities + new_loan

        sim_surplus = sim_income - sim_expenses
        sim_net_worth = sim_assets - sim_liabilities

        if sim_net_worth >= goal:
            sim_goal_score = 90
        elif sim_net_worth >= goal * 0.5:
            sim_goal_score = 60
        else:
            sim_goal_score = 30

        # ----------------------------
        # INSIGHT GENERATION
        # ----------------------------
        insights = []

        if sim_surplus > base_surplus:
            insights.append("Your monthly surplus increased, improving savings capacity.")
        elif sim_surplus < base_surplus:
            insights.append("Your monthly surplus reduced, increasing financial stress.")

        if sim_net_worth > base_net_worth:
            insights.append("Your net worth improved under this scenario.")
        elif sim_net_worth < base_net_worth:
            insights.append("Your net worth declined due to higher costs or liabilities.")

        if sim_goal_score > base_goal_score:
            insights.append("This scenario improves your goal feasibility.")
        elif sim_goal_score < base_goal_score:
            insights.append("This scenario makes your financial goal harder to achieve.")

        return render_template(
            "simulation_result.html",
            base_surplus=base_surplus,
            base_net_worth=base_net_worth,
            base_goal_score=base_goal_score,
            sim_surplus=sim_surplus,
            sim_net_worth=sim_net_worth,
            sim_goal_score=sim_goal_score,
            insights=insights
        )

    # GET request → show simulation page
    return render_template("simulate.html")



@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/market")
def market():
    return render_template("market.html")


@app.route("/bank")
def bank():
    return render_template("bank.html")


# 🔴 THIS PART WAS MISSING
if __name__ == "__main__":
    app.run()




    

