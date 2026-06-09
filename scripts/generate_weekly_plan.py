import json
import random

with open("data/seasonal_vegetables.json", "r") as f:
    seasonal_data = json.load(f)

with open("data/family_profile.json", "r") as f:
    family_profile = json.load(f)

with open("data/protein_options.json", "r") as f:
    protein_data = json.load(f)

month = "June"
vegetables = seasonal_data[month]
breakfast_options = family_profile["breakfast_options"]
protein_options = protein_data["daily_protein_options"]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekly_plan = {}

for day in days:
    weekly_plan[day] = {
        "breakfast": random.choice(breakfast_options),
        "lunch": random.choice(vegetables),
        "dinner": random.choice(["Mixed Dal", "Rajma", "Chole", "Moong Dal", "Arhar Dal"]),
        "protein": random.choice(protein_options)
    }

with open("data/weekly_plan.json", "w") as f:
    json.dump(weekly_plan, f, indent=2)

print("Weekly Meal Plan Generated")
