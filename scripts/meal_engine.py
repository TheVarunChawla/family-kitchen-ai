"""paste and test"""
import json
import random
from datetime import datetime

def get_current_month():
    return datetime.now().strftime("%B")


def load_previous_plan():
    try:
        with open("data/weekly_meal_plan.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}

    if isinstance(data, dict) and "plan" in data:
        return data["plan"]
    return {}

def calculate_day_protein(day_plan, nutrition_db):
    total_protein = 0

    meals = [
        day_plan["breakfast"],
        day_plan["dinner"],
        day_plan["protein_add"]
    ]

    for meal in meals:
        for food, info in nutrition_db.items():

            if food.lower() in meal.lower():
                total_protein += info["protein"]

    return total_protein


def choose_least_used(options, usage_counts, max_count=None):
    choices = [
        option
        for option in options
        if max_count is None or usage_counts.get(option, 0) < max_count
    ]
    if not choices:
        choices = options

    min_count = min(usage_counts.get(option, 0) for option in choices)
    least_used = [
        option
        for option in choices
        if usage_counts.get(option, 0) == min_count
    ]
    return random.choice(least_used)


def choose_with_history(options, usage_counts, previous_penalties=None, max_count=None):
    previous_penalties = previous_penalties or {}
    choices = [
        option
        for option in options
        if max_count is None or usage_counts.get(option, 0) < max_count
    ]
    if not choices:
        choices = options

    ranked = sorted(
        choices,
        key=lambda option: (
            usage_counts.get(option, 0),
            previous_penalties.get(option, 0),
            random.random(),
        ),
    )
    return ranked[0]


def choose_protein_booster(
    breakfast,
    dinner,
    protein_options,
    protein_count,
    previous_protein_penalties,
    nutrition_db,
    low_protein_breakfast,
    high_protein_adds,
):
    protein_floor = 40
    max_repeat = 2
    candidate_pool = [
        protein
        for protein in protein_options
        if protein_count.get(protein, 0) < max_repeat
    ] or protein_options

    if breakfast in low_protein_breakfast:
        candidate_pool = [
            protein
            for protein in candidate_pool
            if protein in high_protein_adds
        ] or high_protein_adds

    if dinner in ["Rajma", "Chole"]:
        preferred = ["Dahi", "Hung Curd", "Sprouts", "Roasted Chana"]
        candidate_pool = [
            protein
            for protein in candidate_pool
            if protein in preferred
        ] or candidate_pool

    ranked = sorted(
        candidate_pool,
        key=lambda item: (
            protein_count.get(item, 0),
            previous_protein_penalties.get(item, 0),
            -nutrition_db.get(item, {}).get("protein", 0),
        )
    )

    for booster in ranked:
        candidate_day = {
            "breakfast": breakfast,
            "dinner": f"{dinner} + Roti",
            "protein_add": booster,
        }
        if calculate_day_protein(candidate_day, nutrition_db) >= protein_floor:
            return booster

    return ranked[0]


def optimize_low_protein_days(plan, nutrition_db):
    TARGET_PROTEIN = 35
    replacement_breakfasts = ["Moong Chilla", "Paneer Chilla", "Besan Chilla"]
    fallback_boosters = ["Paneer", "Soya Granules", "Hung Curd", "Roasted Chana", "Sprouts"]
    low_protein_breakfasts = ["Poha","Upma","Dalia","Aloo Paratha","Gobhi Paratha","Mooli Paratha"]
    breakfast_count = {}
    booster_count = {}

    for meals in plan.values():
        breakfast_count[meals["breakfast"]] = breakfast_count.get(meals["breakfast"], 0) + 1
        booster_count[meals["protein_add"]] = booster_count.get(meals["protein_add"], 0) + 1

    for day, meals in plan.items():
        current_protein = calculate_day_protein(meals, nutrition_db)
        if current_protein < TARGET_PROTEIN:
            if meals["breakfast"] in low_protein_breakfasts:
                old_breakfast = meals["breakfast"]
                breakfast_count[old_breakfast] -= 1
                meals["breakfast"] = choose_least_used(
                    replacement_breakfasts,
                    breakfast_count,
                    2
                )
                breakfast_count[meals["breakfast"]] = breakfast_count.get(meals["breakfast"], 0) + 1

            current_protein = calculate_day_protein(meals, nutrition_db)
            if current_protein < TARGET_PROTEIN:
                booster_pool = [
                    booster
                    for booster in fallback_boosters
                    if (
                        booster_count.get(booster, 0) < 3
                        and (
                            booster != "Soya Granules"
                            or booster_count.get(booster, 0) < 2
                        )
                    )
                ] or fallback_boosters
                ranked_boosters = sorted(
                    booster_pool,
                    key=lambda item: (
                        booster_count.get(item, 0),
                        -nutrition_db.get(item, {}).get("protein", 0),
                    )
                )
                old_booster = meals["protein_add"]
                booster_count[old_booster] = max(booster_count.get(old_booster, 0) - 1, 0)
                meals["protein_add"] = ranked_boosters[0]
                target_reached = False
                for booster in ranked_boosters:
                    boosted_meals = {**meals, "protein_add": booster}
                    if calculate_day_protein(boosted_meals, nutrition_db) >= TARGET_PROTEIN:
                        meals["protein_add"] = booster
                        target_reached = True
                        break

                if not target_reached and booster_pool != fallback_boosters:
                    ranked_boosters = sorted(
                        fallback_boosters,
                        key=lambda item: (
                            booster_count.get(item, 0),
                            -nutrition_db.get(item, {}).get("protein", 0),
                        )
                    )
                    for booster in ranked_boosters:
                        boosted_meals = {**meals, "protein_add": booster}
                        if calculate_day_protein(boosted_meals, nutrition_db) >= TARGET_PROTEIN:
                            meals["protein_add"] = booster
                            break
                booster_count[meals["protein_add"]] = booster_count.get(meals["protein_add"], 0) + 1

    return plan

def load_data():
    with open("data/family_profile.json") as f:
        profile = json.load(f)

    with open("data/seasonal_vegetables.json") as f:
        seasonal = json.load(f)

    with open("data/protein_options.json") as f:
        protein = json.load(f)

    with open("data/nutrition_database.json") as f:
        nutrition = json.load(f)

    return profile, seasonal, protein, nutrition

def build_previous_counts(previous_plan):
    counts = {
        "breakfast": {},
        "lunch": {},
        "dinner": {},
        "protein_add": {},
    }
    same_day = {}

    for day, meals in previous_plan.items():
        breakfast = meals["breakfast"]
        lunch = meals["lunch"].replace(" Sabzi + Roti", "")
        dinner = meals["dinner"].replace(" + Roti", "")
        protein_add = meals["protein_add"]

        counts["breakfast"][breakfast] = counts["breakfast"].get(breakfast, 0) + 1
        counts["lunch"][lunch] = counts["lunch"].get(lunch, 0) + 1
        counts["dinner"][dinner] = counts["dinner"].get(dinner, 0) + 1
        counts["protein_add"][protein_add] = counts["protein_add"].get(protein_add, 0) + 1

        same_day[day] = {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "protein_add": protein_add,
        }

    return counts, same_day


def generate_weekly_plan(previous_plan=None):
    profile, seasonal, protein_data, nutrition_db = load_data()
    previous_plan = previous_plan or {}
    previous_counts, previous_same_day = build_previous_counts(previous_plan)
    month = get_current_month()
    vegetables = seasonal.get(month, seasonal["June"])
    protein_options = [p["name"] for p in protein_data["daily_protein_options"]]
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday_breakfast = profile["breakfast_weekday"]
    weekend_breakfast = profile["breakfast_weekend"]
    dal_options = profile["dal_options"]
    high_protein_breakfast = ["Moong Chilla","Paneer Chilla","Besan Chilla"]
    low_protein_breakfast  = ["Poha","Upma","Dalia","Aloo Paratha","Gobhi Paratha","Mooli Paratha"]
    high_protein_adds      = ["Paneer","Soya Granules","Hung Curd","Sprouts","Roasted Chana"]
    plan = {}
    breakfast_count  = {}
    vegetable_count  = {}
    protein_count    = {}
    dinner_count     = {}
    high_breakfast_days = 0

    for day in days:
        # BREAKFAST
        if day in ["Saturday","Sunday"]:
            if high_breakfast_days < 4:
                breakfast_penalties = dict(previous_counts["breakfast"])
                if day in previous_same_day:
                    prev_breakfast = previous_same_day[day]["breakfast"]
                    breakfast_penalties[prev_breakfast] = breakfast_penalties.get(prev_breakfast, 0) + 3
                breakfast = choose_with_history(high_protein_breakfast, breakfast_count, breakfast_penalties, 2)
                high_breakfast_days += 1
            else:
                breakfast_penalties = dict(previous_counts["breakfast"])
                if day in previous_same_day:
                    prev_breakfast = previous_same_day[day]["breakfast"]
                    breakfast_penalties[prev_breakfast] = breakfast_penalties.get(prev_breakfast, 0) + 3
                breakfast = choose_with_history(weekend_breakfast, breakfast_count, breakfast_penalties, 1)
        else:
            if high_breakfast_days < 4:
                choices = [b for b in weekday_breakfast
                           if b in high_protein_breakfast and breakfast_count.get(b, 0) < 2]
                if choices:
                    breakfast_penalties = dict(previous_counts["breakfast"])
                    if day in previous_same_day:
                        prev_breakfast = previous_same_day[day]["breakfast"]
                        breakfast_penalties[prev_breakfast] = breakfast_penalties.get(prev_breakfast, 0) + 3
                    breakfast = choose_with_history(choices, breakfast_count, breakfast_penalties)
                    high_breakfast_days += 1
                else:
                    breakfast_penalties = dict(previous_counts["breakfast"])
                    if day in previous_same_day:
                        prev_breakfast = previous_same_day[day]["breakfast"]
                        breakfast_penalties[prev_breakfast] = breakfast_penalties.get(prev_breakfast, 0) + 3
                    breakfast = choose_with_history(weekday_breakfast, breakfast_count, breakfast_penalties, 2)
            else:
                choices = [b for b in weekday_breakfast if breakfast_count.get(b, 0) < 2]
                breakfast_penalties = dict(previous_counts["breakfast"])
                if day in previous_same_day:
                    prev_breakfast = previous_same_day[day]["breakfast"]
                    breakfast_penalties[prev_breakfast] = breakfast_penalties.get(prev_breakfast, 0) + 3
                breakfast = choose_with_history(choices if choices else weekday_breakfast, breakfast_count, breakfast_penalties)
        breakfast_count[breakfast] = breakfast_count.get(breakfast, 0) + 1

        # LUNCH
        available_veg = [v for v in vegetables if vegetable_count.get(v, 0) < 2] or vegetables
        vegetable_penalties = dict(previous_counts["lunch"])
        if day in previous_same_day:
            prev_lunch = previous_same_day[day]["lunch"]
            vegetable_penalties[prev_lunch] = vegetable_penalties.get(prev_lunch, 0) + 3
        sabzi = choose_with_history(available_veg, vegetable_count, vegetable_penalties)
        vegetable_count[sabzi] = vegetable_count.get(sabzi, 0) + 1

        # DINNER
        if day == "Tuesday":
            dinner = "Rajma"
        elif day == "Friday":
            dinner = "Chole"
        elif day == "Sunday":
            dinner = "Kadhi"
        else:
            available_dals = [d for d in dal_options if dinner_count.get(d, 0) < 2] or dal_options
            dinner_penalties = dict(previous_counts["dinner"])
            if day in previous_same_day:
                prev_dinner = previous_same_day[day]["dinner"]
                dinner_penalties[prev_dinner] = dinner_penalties.get(prev_dinner, 0) + 3
            dinner = choose_with_history(available_dals, dinner_count, dinner_penalties)
        dinner_count[dinner] = dinner_count.get(dinner, 0) + 1

        # PROTEIN ADD
        protein_add = choose_protein_booster(
            breakfast,
            dinner,
            protein_options,
            protein_count,
            dict(previous_counts["protein_add"]),
            nutrition_db,
            low_protein_breakfast,
            high_protein_adds,
        )
        protein_count[protein_add] = protein_count.get(protein_add, 0) + 1

        plan[day] = {
            "breakfast":   breakfast,
            "lunch":       f"{sabzi} Sabzi + Roti",
            "dinner":      f"{dinner} + Roti",
            "protein_add": protein_add
        }

    plan = optimize_low_protein_days(plan, nutrition_db)
    return plan, month, vegetables, nutrition_db

def generate_shopping_list(plan, vegetables):
    sabzis, dals, proteins = set(), set(), set()
    dal_keywords = ["Dal","Rajma","Chole","Kadhi"]
    for day_plan in plan.values():
        sabzis.add(day_plan["lunch"].replace(" Sabzi + Roti",""))
        dinner = day_plan["dinner"].replace(" + Roti","")
        for kw in dal_keywords:
            if kw in dinner:
                dals.add(dinner)
                break
        proteins.add(day_plan["protein_add"])
    essentials = ["Roti Atta","Rice","Milk","Dahi","Cooking Oil","Onion","Tomato","Ginger-Garlic"]
    return {"vegetables": sorted(sabzis), "dals_legumes": sorted(dals),
            "protein_sources": sorted(proteins), "kitchen_essentials": essentials}

def calculate_protein_score(plan, nutrition_db):
    """
    Calculate weekly protein score using complete day protein:
    breakfast + dinner + protein boosters.
    """

    daily_protein = {}
    total_week_protein = 0

    for day, meals in plan.items():
        protein = calculate_day_protein(
            meals,
            nutrition_db
        )

        daily_protein[day] = protein
        total_week_protein += protein

    average_daily_protein = round(
        total_week_protein / len(plan),
        1
    )

    # Protein score out of 10
    # 60g average daily protein = 10/10
    score = min(
        10,
        round((average_daily_protein / 60) * 10, 1)
    )

    return (
        score,
        average_daily_protein,
        daily_protein
    )

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
    previous_plan = load_previous_plan()
    plan, month, veg, nutrition_db = generate_weekly_plan(previous_plan)
    shopping = generate_shopping_list(plan, veg)
    score, avg, daily_protein = calculate_protein_score(
        plan,
        nutrition_db
    )
    tips, family_tip = generate_health_tips(plan)
    with open("data/weekly_meal_plan.json", "w") as f:
        json.dump({"month": month, "plan": plan, "shopping": shopping,
                   "protein_score": score, "protein_avg_daily_g": avg,
                   "daily_protein": daily_protein,
                   "health_tips": tips, "family_tip": family_tip}, f, indent=2)
    print(f"Weekly plan generated for {month}")
