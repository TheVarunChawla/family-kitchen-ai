import json


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

LOW_PROTEIN_TARGET = 30
GOOD_PROTEIN_TARGET = 40
STRONG_PROTEIN_TARGET = 50
FAMILY_AVG_PROTEIN_TARGET = 60

DIABETES_RISKY_BREAKFASTS = {
    "Poha",
    "Upma",
    "Dalia",
    "Aloo Paratha",
    "Gobhi Paratha",
    "Mooli Paratha",
}

DIABETES_FRIENDLY_BREAKFASTS = {
    "Moong Chilla",
    "Paneer Chilla",
    "Besan Chilla",
}

HIGH_BP_LIGHT_DINNERS = {
    "Moong Dal",
    "Masoor Dal",
    "Mixed Dal",
    "Arhar Dal",
    "Chana Dal",
    "Kadhi",
}

HIGH_QUALITY_BOOSTERS = {
    "Paneer",
    "Soya Granules",
    "Hung Curd",
    "Sprouts",
    "Roasted Chana",
}


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def detect_foods(text, nutrition_db):
    text_lower = text.lower()
    return [
        (food, info)
        for food, info in nutrition_db.items()
        if food.lower() in text_lower
    ]


def calculate_day_protein(day_plan, nutrition_db):
    total = 0
    for section in ["breakfast", "dinner", "protein_add"]:
        for _, info in detect_foods(day_plan.get(section, ""), nutrition_db):
            total += info["protein"]
    return total


def extract_lunch_vegetable(lunch):
    return (
        lunch.replace(" Sabzi + Roti", "")
        .replace(" + Roti", "")
        .strip()
    )


def extract_dinner_name(dinner):
    return dinner.replace(" + Roti", "").replace(" + Salad", "").strip()


def grade_for_score(score):
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Very Good"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Needs Attention"
    return "High Priority"


def analyze_week(data, family_profile, nutrition_db):
    plan = data["plan"]
    daily_protein = data.get("daily_protein") or {
        day: calculate_day_protein(day_plan, nutrition_db)
        for day, day_plan in plan.items()
    }

    breakfasts = [plan[day]["breakfast"] for day in DAYS if day in plan]
    dinners = [extract_dinner_name(plan[day]["dinner"]) for day in DAYS if day in plan]
    boosters = [plan[day]["protein_add"] for day in DAYS if day in plan]
    vegetables = [
        extract_lunch_vegetable(plan[day]["lunch"])
        for day in DAYS
        if day in plan
    ]

    avg_protein = round(sum(daily_protein.values()) / len(daily_protein), 1)
    low_protein_days = [day for day, grams in daily_protein.items() if grams < LOW_PROTEIN_TARGET]
    good_protein_days = [day for day, grams in daily_protein.items() if grams >= GOOD_PROTEIN_TARGET]
    strong_protein_days = [day for day, grams in daily_protein.items() if grams >= STRONG_PROTEIN_TARGET]

    risky_breakfast_days = [
        day
        for day in DAYS
        if day in plan and plan[day]["breakfast"] in DIABETES_RISKY_BREAKFASTS
    ]
    diabetes_friendly_days = [
        day
        for day in DAYS
        if day in plan and plan[day]["breakfast"] in DIABETES_FRIENDLY_BREAKFASTS
    ]

    high_bp_light_dinner_days = [
        day
        for day in DAYS
        if day in plan and extract_dinner_name(plan[day]["dinner"]) in HIGH_BP_LIGHT_DINNERS
    ]
    high_quality_booster_days = [
        day
        for day in DAYS
        if day in plan and plan[day]["protein_add"] in HIGH_QUALITY_BOOSTERS
    ]

    breakfast_variety = len(set(breakfasts))
    vegetable_variety = len(set(vegetables))
    booster_variety = len(set(boosters))
    dinner_variety = len(set(dinners))

    protein_score = (
        min(avg_protein / FAMILY_AVG_PROTEIN_TARGET, 1) * 20
        + (len(good_protein_days) / 7) * 10
        + (len(strong_protein_days) / 7) * 5
    )

    diabetes_score = max(0, 20 - (len(risky_breakfast_days) * 4))
    vegetable_score = min(vegetable_variety / 6, 1) * 15
    bp_score = (len(high_bp_light_dinner_days) / 7) * 10
    booster_score = (len(high_quality_booster_days) / 7) * 8

    variety_score = (
        min(breakfast_variety / 5, 1) * 4
        + min(vegetable_variety / 6, 1) * 4
        + min(booster_variety / 5, 1) * 4
        + min(dinner_variety / 6, 1) * 4
    )

    repeat_penalty = 0
    max_breakfast_repeat = max((breakfasts.count(item) for item in set(breakfasts)), default=0)
    max_booster_repeat = max((boosters.count(item) for item in set(boosters)), default=0)
    if max_breakfast_repeat > 3:
        repeat_penalty += 2
    if max_booster_repeat > 3:
        repeat_penalty += 2

    score = round(
        protein_score
        + diabetes_score
        + vegetable_score
        + bp_score
        + booster_score
        + variety_score
        - repeat_penalty
    )
    score = max(0, min(score, 100))

    achievements = []
    alerts = []
    focus_areas = []

    if len(low_protein_days) == 0:
        achievements.append("All days stayed above the minimum protein floor")
    else:
        alerts.append(f"{len(low_protein_days)} days fell below {LOW_PROTEIN_TARGET}g protein")

    if len(good_protein_days) >= 5:
        achievements.append("Most days reached a strong vegetarian protein range")
    else:
        focus_areas.append("Raise more days above 40g protein")

    if len(risky_breakfast_days) == 0:
        achievements.append("Breakfasts were diabetes-friendly all week")
    else:
        alerts.append(f"{len(risky_breakfast_days)} high-carb breakfasts need balancing")

    if vegetable_variety >= 5:
        achievements.append("Good seasonal vegetable variety")
    else:
        focus_areas.append("Add at least 5 different lunch vegetables")

    if max_booster_repeat > 3:
        focus_areas.append("Rotate protein boosters more evenly")

    if max_breakfast_repeat > 3:
        focus_areas.append("Rotate high-protein breakfasts more evenly")

    if len(high_bp_light_dinner_days) < 4:
        focus_areas.append("Add more light dal or kadhi dinners for BP support")

    member_recommendations = build_member_recommendations(
        family_profile,
        avg_protein,
        len(risky_breakfast_days),
        len(high_bp_light_dinner_days),
        len(low_protein_days),
    )

    return {
        "health_score": score,
        "grade": grade_for_score(score),
        "average_daily_protein_g": avg_protein,
        "high_protein_days": len(good_protein_days),
        "strong_protein_days": len(strong_protein_days),
        "low_protein_days": len(low_protein_days),
        "diabetes_friendly_breakfast_days": len(diabetes_friendly_days),
        "high_carb_breakfast_days": len(risky_breakfast_days),
        "vegetable_variety_count": vegetable_variety,
        "breakfast_variety_count": breakfast_variety,
        "booster_variety_count": booster_variety,
        "component_scores": {
            "protein": round(protein_score, 1),
            "diabetes": round(diabetes_score, 1),
            "vegetables": round(vegetable_score, 1),
            "bp_support": round(bp_score, 1),
            "protein_boosters": round(booster_score, 1),
            "variety": round(variety_score, 1),
            "repeat_penalty": repeat_penalty,
        },
        "achievements": achievements,
        "alerts": alerts,
        "focus_areas": focus_areas,
        "member_recommendations": member_recommendations,
    }


def build_member_recommendations(
    family_profile,
    avg_protein,
    high_carb_breakfast_count,
    high_bp_light_dinner_count,
    low_protein_day_count,
):
    recommendations = {}

    for member in family_profile["members"]:
        name = member["name"]
        conditions = set(member.get("conditions", []))
        priority = member.get("protein_priority", "normal")

        if "Muscle Loss" in conditions or priority == "high":
            if avg_protein < FAMILY_AVG_PROTEIN_TARGET:
                recommendations[name] = "Keep a protein booster daily; aim for one extra dal, paneer, or soya serving."
            else:
                recommendations[name] = "Protein trend is strong; keep resistance exercise and daily boosters consistent."
        elif "Diabetes" in conditions:
            if high_carb_breakfast_count:
                recommendations[name] = "Pair any poha, upma, or paratha with curd, sprouts, or paneer."
            else:
                recommendations[name] = "Breakfast pattern is glucose-friendly; keep chilla and dal-based meals frequent."
        elif "High BP" in conditions:
            if high_bp_light_dinner_count < 4:
                recommendations[name] = "Prefer lighter dal or kadhi dinners more often and keep pickles/namkeen low."
            else:
                recommendations[name] = "Dinner pattern supports BP; continue limiting salty snacks and pickles."
        elif "Overweight" in conditions:
            recommendations[name] = "Keep dinner portions lighter and add a post-dinner walk on most days."
        else:
            recommendations[name] = "Maintain the current variety and include curd or sprouts regularly."

    return recommendations


if __name__ == "__main__":
    data = load_json("data/weekly_meal_plan.json")
    family_profile = load_json("data/family_profile.json")
    nutrition_db = load_json("data/nutrition_database.json")

    data["health_analysis"] = analyze_week(data, family_profile, nutrition_db)

    with open("data/weekly_meal_plan.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Health analysis added to weekly_meal_plan.json")
