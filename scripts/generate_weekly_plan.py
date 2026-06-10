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

breakfast_weekday = family_profile["breakfast_weekday"]
breakfast_weekend = family_profile["breakfast_weekend"]
dal_options       = family_profile["dal_options"]
special_dinner    = family_profile["special_dinner"]
protein_options   = [p["name"] for p in protein_data["daily_protein_options"]]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekly_plan = {}

for day in days:
    is_weekend = day in ["Saturday", "Sunday"]
    breakfast  = random.choice(breakfast_weekend if is_weekend else breakfast_weekday)

    # Special dinner twice a week, dal on other days
    if day in ["Tuesday", "Friday"]:
        dinner = random.choice(special_dinner)
    else:
        dinner = random.choice(dal_options)

    weekly_plan[day] = {
        "breakfast":   breakfast,
        "lunch":       random.choice(vegetables),
        "dinner":      dinner,
        "protein_add": random.choice(protein_options)
    }

with open("data/weekly_meal_plan.json", "w") as f:
    json.dump(weekly_plan, f, indent=2)

print("Weekly Meal Plan Generated")
