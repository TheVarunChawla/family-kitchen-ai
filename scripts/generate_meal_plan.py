import json
import random

with open("data/seasonal_vegetables.json", "r") as f:
    seasonal_data = json.load(f)

month = "June"
vegetables = seasonal_data[month]

meal_plan = {
    "breakfast": [
        random.choice(["Poha", "Upma", "Dalia", "Moong Chilla", "Besan Chilla"]),
        random.choice(["Poha", "Upma", "Dalia", "Moong Chilla", "Besan Chilla"]),
        random.choice(["Poha", "Upma", "Dalia", "Moong Chilla", "Besan Chilla"])
    ],
    "lunch": vegetables[:3],
    "dinner": [
        "Mixed Dal",
        "Rajma",
        "Chole"
    ],
    "protein_mission": [
        "Hung Curd",
        "Paneer",
        "Soya Granules"
    ]
}

with open("data/meal_plan.json", "w") as f:
    json.dump(meal_plan, f, indent=2)

print("Meal Plan Generated")
