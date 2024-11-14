from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64

app = Flask(__name__)

def run_simulation(lifespan, initial_cost, maintenance_budget, major_repair_cost,
                   repair_prob, replacement_cost, replacement_threshold, insurance_contribution,
                   user_intensity, decision_margin, specific_year, specific_major_repair_cost):
    
    minor_repair_cost_range = (200 * user_intensity, 400 * user_intensity)
    adjusted_repair_prob = repair_prob * user_intensity
    cumulative_repairs = []
    pool_balance = 0
    results = {
        "Year": [], "Minor Repairs ($)": [], "Major Repairs ($)": [], 
        "Total Repairs ($)": [], "Cumulative Repair Cost ($)": [],
        "Replacement Decision": [], "Pool Balance ($)": []
    }

    for year in range(1, lifespan + 1):
        minor_repair = np.random.randint(int(minor_repair_cost_range[0]), int(minor_repair_cost_range[1]))
        major_repair = specific_major_repair_cost if year == specific_year else (major_repair_cost if np.random.rand() < adjusted_repair_prob else 0)
        total_repair = minor_repair + major_repair
        cumulative_cost = total_repair + (cumulative_repairs[-1] if cumulative_repairs else 0)
        cumulative_repairs.append(cumulative_cost)
        
        replacement_threshold_value = replacement_cost * replacement_threshold
        review_margin_value = replacement_threshold_value * (1 - decision_margin)
        
        if cumulative_cost >= replacement_threshold_value:
            replace = "Yes"
        elif cumulative_cost >= review_margin_value:
            replace = "Review Needed"
        else:
            replace = "No"
        
        pool_balance += insurance_contribution - total_repair
        if replace == "Yes":
            pool_balance -= replacement_cost
        
        results["Year"].append(year)
        results["Minor Repairs ($)"].append(minor_repair)
        results["Major Repairs ($)"].append(major_repair)
        results["Total Repairs ($)"].append(total_repair)
        results["Cumulative Repair Cost ($)"].append(cumulative_cost)
        results["Replacement Decision"].append(replace)
        results["Pool Balance ($)"].append(pool_balance)

    df = pd.DataFrame(results)

    fig1, ax1 = plt.subplots()
    ax1.plot(df["Year"], df["Cumulative Repair Cost ($)"], label="Cumulative Repair Cost", color='blue', marker='o')
    ax1.axhline(y=replacement_cost * replacement_threshold, color='red', linestyle='--', label="Replacement Threshold")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Cumulative Repair Cost ($)")
    ax1.legend()
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()

    fig2, ax2 = plt.subplots()
    ax2.plot(df["Year"], df["Pool Balance ($)"], label="Insurance Pool Balance", color='green', marker='o')
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Insurance Pool Balance ($)")
    ax2.legend()
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()

    return df.to_html(index=False), plot_url1, plot_url2

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation_route():
    lifespan = int(request.form['lifespan'])
    initial_cost = float(request.form['initial_cost'])
    maintenance_budget = float(request.form['maintenance_budget'])
    major_repair_cost = float(request.form['major_repair_cost'])
    repair_prob = float(request.form['repair_prob'])
    replacement_cost = float(request.form['replacement_cost'])
    replacement_threshold = float(request.form['replacement_threshold']) / 100
    insurance_contribution = float(request.form['insurance_contribution'])
    user_intensity = float(request.form['user_intensity'])
    decision_margin = float(request.form['decision_margin']) / 100
    specific_year = int(request.form['specific_year'])
    specific_major_repair_cost = float(request.form['specific_major_repair_cost'])

    simulation_output, plot_url1, plot_url2 = run_simulation(
        lifespan, initial_cost, maintenance_budget, major_repair_cost, repair_prob,
        replacement_cost, replacement_threshold, insurance_contribution,
        user_intensity, decision_margin, specific_year, specific_major_repair_cost
    )

    return render_template('result.html', simulation_output=simulation_output, plot_url1=plot_url1, plot_url2=plot_url2)

if __name__ == '__main__':
    app.run(debug=True)
