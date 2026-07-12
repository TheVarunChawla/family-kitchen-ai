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
    "Methi Paratha",
    "Vegetable Daliya",
}

DIABETES_FRIENDLY_BREAKFASTS = {
    "Moong Chilla",
    "Paneer Chilla",
    "Besan Chilla",
    "Sprouts Chilla",
    "Oats Chilla",
}

HIGH_BP_LIGHT_DINNERS = {
    "Moong Dal",
    "Masoor Dal",
    "Mixed Dal",
    "Arhar Dal",
    "Chana Dal",
    "Kadhi",
    "Urad Dal",
    "Sambar",
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
    for section in ["breakfast", "lunch", "dinner", "protein_add"]:
        for _, info in detect_foods(day_plan.get(section, ""), nutrition_db):
            total += info["protein"]
    return total


def extract_lunch_vegetable(lunch):
    return lunch.split(" + ")[0].split()[0].strip()


def extract_dinner_name(dinner):
    return dinner.replace(" + Roti", "").replace(" + Salad", "").strip()


def format_days(days):
    if not days:
        return "no days"
    if len(days) == 1:
        return days[0]
    return ", ".join(days[:-1]) + f" and {days[-1]}"


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
    lightest_protein_days = [
        day
        for day, _ in sorted(daily_protein.items(), key=lambda item: item[1])[:2]
    ]

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
    heavier_legume_days = [
        day
        for day in DAYS
        if day in plan and extract_dinner_name(plan[day]["dinner"]) in {"Rajma", "Chole"}
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

    action_plan = build_action_plan(
        daily_protein,
        risky_breakfast_days,
        heavier_legume_days,
        max_booster_repeat,
        max_breakfast_repeat,
    )

    member_recommendations = build_member_recommendations(
        family_profile,
        avg_protein,
        risky_breakfast_days,
        heavier_legume_days,
        lightest_protein_days,
    )

    family_goal = build_family_goal(
        avg_protein,
        risky_breakfast_days,
        vegetable_variety,
        max_booster_repeat,
        max_breakfast_repeat,
        good_protein_days,
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
        "weekly_action_plan": action_plan,
        "member_recommendations": member_recommendations,
        "family_goal": family_goal,
    }


def build_action_plan(
    daily_protein,
    risky_breakfast_days,
    heavier_legume_days,
    max_booster_repeat,
    max_breakfast_repeat,
):
    actions = []

    if risky_breakfast_days:
        actions.append(
            f"On {format_days(risky_breakfast_days)}, pair the carb-heavy breakfast with curd, sprouts, or paneer."
        )

    if heavier_legume_days:
        actions.append(
            f"On {format_days(heavier_legume_days)}, keep dinner salt light and add a 10-minute walk after eating."
        )

    light_days = [
        day
        for day, grams in sorted(daily_protein.items(), key=lambda item: item[1])[:2]
        if grams < STRONG_PROTEIN_TARGET
    ]
    if light_days:
        actions.append(
            f"Add an extra curd, sprouts, or roasted chana snack on {format_days(light_days)} to lift lighter protein days."
        )

    if max_booster_repeat > 3:
        actions.append("Rotate Soya Granules with Paneer, Hung Curd, Sprouts, or Roasted Chana.")

    if max_breakfast_repeat > 3:
        actions.append("Rotate Paneer Chilla with Moong or Besan Chilla to improve breakfast variety.")

    if not actions:
        actions.append("Keep this plan steady and repeat the same protein-plus-vegetable structure next week.")

    return actions[:3]


def build_family_goal(
    avg_protein,
    risky_breakfast_days,
    vegetable_variety,
    max_booster_repeat,
    max_breakfast_repeat,
    good_protein_days,
):
    """Pick one dynamic, week-specific family goal instead of a fixed line.

    Priority: fix the biggest real gap this week (diabetes risk > protein >
    variety); if the week is genuinely clean, say so with an actual number
    instead of a generic filler every time.
    """
    if risky_breakfast_days:
        return (
            f"Pair {format_days(risky_breakfast_days)}'s carb-heavy breakfast "
            "with curd, sprouts, or paneer to blunt the sugar spike."
        )

    if avg_protein < FAMILY_AVG_PROTEIN_TARGET:
        gap = round(FAMILY_AVG_PROTEIN_TARGET - avg_protein, 1)
        return f"Close the {gap}g/day protein gap — add one extra curd, sprouts, or roasted chana snack daily."

    if max_booster_repeat > 3:
        return "Rotate protein boosters more evenly instead of leaning on one snack all week."

    if max_breakfast_repeat > 3:
        return "Rotate breakfasts more evenly — variety, not just protein, keeps this sustainable."

    if vegetable_variety < 5:
        return "Add at least one new lunch vegetable this week to widen variety."

    return (
        f"Protein averaged {avg_protein}g/day with {good_protein_days} strong days — "
        "hold this pattern and keep the variety going next week."
    )


def build_member_recommendations(
    family_profile,
    avg_protein,
    risky_breakfast_days,
    heavier_legume_days,
    lightest_protein_days,
):
    recommendations = {}

    for member in family_profile["members"]:
        name = member["name"]
        conditions = set(member.get("conditions", []))
        priority = member.get("protein_priority", "normal")
        advice = []

        if "Muscle Loss" in conditions or priority == "high":
            if avg_protein < FAMILY_AVG_PROTEIN_TARGET:
                advice.append(
                    f"Use an extra curd, sprouts, or paneer snack on {format_days(lightest_protein_days)} for muscle support."
                )
            else:
                advice.append("Protein trend is strong; keep daily boosters and light strength work consistent.")

        if "Diabetes" in conditions:
            if risky_breakfast_days:
                advice.append(
                    f"On {format_days(risky_breakfast_days)}, pair breakfast with curd, sprouts, or paneer."
                )
            else:
                advice.append("Breakfast pattern is glucose-friendly; keep chilla and dal-based meals frequent.")

        if "High BP" in conditions:
            if heavier_legume_days:
                advice.append(
                    f"On {format_days(heavier_legume_days)}, keep salt, pickle, and namkeen low."
                )
            else:
                advice.append("Dinner pattern supports BP; continue limiting salty snacks and pickles.")

        if "Overweight" in conditions:
            advice.append("Keep dinner portions lighter and add a post-dinner walk on most days.")

        if not advice:
            advice.append("Maintain the current variety and include curd or sprouts regularly.")

        recommendations[name] = " ".join(advice[:2])

    return recommendations


if __name__ == "__main__":
    data = load_json("data/weekly_meal_plan.json")
    family_profile = load_json("data/family_profile.json")
    nutrition_db = load_json("data/nutrition_database.json")

    data["health_analysis"] = analyze_week(data, family_profile, nutrition_db)

    with open("data/weekly_meal_plan.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Health analysis added to weekly_meal_plan.json")
