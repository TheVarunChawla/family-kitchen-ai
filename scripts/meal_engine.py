"""
Core meal planning engine for Parivaar Nutrition AI.
Generates a health-aware 7-day plan using seasonal vegetables and family rules.
"""
import json
import random
from datetime import datetime

def load_data():
    with open("data/family_profile.json") as f:
        profile = json.load(f)
    with open("data/seasonal_vegetables.json") as f:
        seasonal = json.load(f)
    with open("data/protein_options.json") as f:
        protein = json.load(f)
    return profile, seasonal, protein

def get_current_month():
    return datetime.now().strftime("%B")

def generate_weekly_plan():
    profile, seasonal, protein_data = load_data()

    month = get_current_month()
    vegetables = seasonal.get(month, seasonal["June"])

    protein_options = [
        p["name"] for p in protein_data["daily_protein_options"]
    ]

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday_breakfast = profile["breakfast_weekday"]
    weekend_breakfast = profile["breakfast_weekend"]
    dal_options = profile["dal_options"]
    special_dinner = profile["special_dinner"]

    # Protein intelligence
    high_protein_breakfast = [
        "Moong Chilla",
        "Paneer Chilla"
    ]

    low_protein_breakfast = [
        "Poha",
        "Upma",
        "Dalia",
        "Aloo Paratha",
        "Gobhi Paratha"
    ]

    high_protein_adds = [
        "Paneer",
        "Soya Granules",
        "Hung Curd",
        "Sprouts"
    ]

    plan = {}

    breakfast_count = {}
    vegetable_count = {}
    protein_count = {}

    high_breakfast_days = 0


    for day in days:

        # =============================
        # BREAKFAST SELECTION
        # =============================

        if day in ["Saturday", "Sunday"]:

            breakfast = random.choice(
                weekend_breakfast
            )

        else:

            # Ensure a minimum of 3 high-protein breakfasts
            if high_breakfast_days < 3:

                choices = [
                    b for b in weekday_breakfast
                    if b in high_protein_breakfast
                ]

                if choices:
                    breakfast = random.choice(choices)
                    high_breakfast_days += 1
                else:
                    breakfast = random.choice(weekday_breakfast)

            else:

                choices = [
                    b for b in weekday_breakfast
                    if breakfast_count.get(b, 0) < 2
                ]

                breakfast = random.choice(choices)

        breakfast_count[breakfast] = (
            breakfast_count.get(breakfast, 0) + 1
        )


        # =============================
        # LUNCH VEGETABLE SELECTION
        # =============================

        available_veg = [
            veg for veg in vegetables
            if vegetable_count.get(veg, 0) < 2
        ]

        if not available_veg:
            available_veg = vegetables

        sabzi = random.choice(available_veg)

        vegetable_count[sabzi] = (
            vegetable_count.get(sabzi, 0) + 1
        )


        # =============================
        # DINNER SELECTION
        # =============================

        if day in ["Tuesday", "Friday"]:

            dinner = random.choice(
                special_dinner
            )

        else:

            dinner = random.choice(
                dal_options
            )


        # =============================
        # PROTEIN BOOSTER SELECTION
        # =============================

        if breakfast in low_protein_breakfast:

            choices = [
                p for p in protein_options
                if p in high_protein_adds
                and protein_count.get(p, 0) < 2
            ]

        else:

            choices = [
                p for p in protein_options
                if protein_count.get(p, 0) < 2
            ]


        if not choices:
            choices = protein_options


        protein_add = random.choice(
            choices
        )

        protein_count[protein_add] = (
            protein_count.get(protein_add, 0) + 1
        )


        # =============================
        # SAVE DAILY PLAN
        # =============================

        plan[day] = {

            "breakfast": breakfast,

            "lunch": f"{sabzi} Sabzi + Roti",

            "dinner": f"{dinner} + Roti",

            "protein_add": protein_add
        }


    return plan, month, vegetables

def generate_shopping_list(plan, vegetables):
    sabzis = set()
    dals = set()
    proteins = set()

    dal_keywords = ["Dal", "Rajma", "Chole", "Kadhi"]
    protein_keywords = ["Paneer", "Hung Curd", "Chana", "Soya", "Sprouts", "Peanuts", "Dahi"]

    for day_plan in plan.values():
        lunch = day_plan["lunch"].replace(" Sabzi + Roti", "")
        sabzis.add(lunch)

        dinner = day_plan["dinner"].replace(" + Roti", "")
        for kw in dal_keywords:
            if kw in dinner:
                dals.add(dinner)
                break

        p = day_plan["protein_add"]
        proteins.add(p)

    essentials = ["Roti Atta", "Rice", "Milk", "Dahi", "Cooking Oil", "Onion", "Tomato", "Ginger-Garlic"]

    return {
        "vegetables": sorted(sabzis),
        "dals_legumes": sorted(dals),
        "protein_sources": sorted(proteins),
        "kitchen_essentials": essentials
    }

def calculate_protein_score(plan):
    protein_data = {
        "Hung Curd": 11, "Paneer": 18, "Roasted Chana": 19,
        "Soya Granules": 52, "Sprouts": 9, "Moong Dal": 24,
        "Peanuts": 26, "Dahi": 4, "Mixed Dal": 9, "Arhar Dal": 8,
        "Masoor Dal": 9, "Chana Dal": 13, "Moong Dal": 24
    }
    weekly_adds = [day["protein_add"] for day in plan.values()]
    total = sum(protein_data.get(p, 8) for p in weekly_adds)
    avg_daily = total // 7
    # Score out of 10
    score = min(10, round(avg_daily / 8))
    return score, avg_daily

def generate_health_tips(plan):
    tips = {
        "Dad":     "Add Roasted Chana as evening snack — helps muscle recovery",
        "Mom":     "Reduce namkeen & pickles — high salt worsens BP",
        "Sister1": "20-minute walk after dinner — best for blood sugar",
        "Sister2": "Add sprouts to lunch twice this week",
        "Varun":   "Add Soya Granules to sabzi 2x this week for protein boost",
        "Wife":    "Include Dahi daily — good for gut health"
    }
    family_tip = "Replace evening biscuits with Roasted Chana or Peanuts"
    return tips, family_tip

if __name__ == "__main__":
    plan, month, veg = generate_weekly_plan()
    shopping = generate_shopping_list(plan, veg)
    score, avg = calculate_protein_score(plan)
    tips, family_tip = generate_health_tips(plan)

    with open("data/weekly_meal_plan.json", "w") as f:
        json.dump({
            "month": month,
            "plan": plan,
            "shopping": shopping,
            "protein_score": score,
            "protein_avg_daily_g": avg,
            "health_tips": tips,
            "family_tip": family_tip
        }, f, indent=2)

    print(f"✅ Weekly plan generated for {month}")
