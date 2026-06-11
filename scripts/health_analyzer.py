import json


def analyze_week(plan):
    score = 100
    alerts = []
    achievements = []

    high_protein_days = 0
    low_protein_days = 0

    protein_target = 30

    # Protein values
    protein_db = {
        "Moong Chilla": 12,
        "Paneer Chilla": 14,
        "Besan Chilla": 10,
        "Paneer": 18,
        "Soya Granules": 25,
        "Hung Curd": 11,
        "Sprouts": 8,
        "Dahi": 6,
        "Moong Dal": 7,
        "Masoor Dal": 9,
        "Chana Dal": 13,
        "Mixed Dal": 9,
        "Arhar Dal": 8,
        "Rajma": 13,
        "Chole": 14
    }

    vegetables = set()
    high_carb_breakfast = 0

    for day, meals in plan.items():

        daily_protein = 0

        for item in [
            meals["breakfast"],
            meals["dinner"],
            meals["protein_add"]
        ]:

            for food, value in protein_db.items():

                if food.lower() in item.lower():
                    daily_protein += value

        if daily_protein >= protein_target:
            high_protein_days += 1
        else:
            low_protein_days += 1

        # Diabetes check
        if meals["breakfast"] in [
            "Poha",
            "Upma",
            "Aloo Paratha",
            "Gobhi Paratha",
            "Mooli Paratha"
        ]:
            high_carb_breakfast += 1

        vegetables.add(
            meals["lunch"].replace(" Sabzi + Roti", "")
        )


    # Scoring Logic

    if low_protein_days > 2:
        score -= 15
        alerts.append(
            f"{low_protein_days} days had low protein intake"
        )
    else:
        achievements.append(
            "Good weekly protein consistency"
        )


    if high_carb_breakfast > 2:
        score -= 10
        alerts.append(
            "Too many high-carb breakfasts for diabetic family members"
        )
    else:
        achievements.append(
            "Breakfast choices were diabetes friendly"
        )


    if len(vegetables) < 4:
        score -= 10
        alerts.append(
            "Increase vegetable variety next week"
        )
    else:
        achievements.append(
            "Excellent vegetable variety"
        )


    if score >= 85:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Average"
    else:
        grade = "Needs Improvement"


    return {
        "health_score": score,
        "grade": grade,
        "high_protein_days": high_protein_days,
        "low_protein_days": low_protein_days,
        "achievements": achievements,
        "alerts": alerts
    }


if __name__ == "__main__":

    # Load existing weekly report
    with open("data/weekly_meal_plan.json", "r") as f:
        data = json.load(f)


    # Run AI health analysis
    report = analyze_week(
        data["plan"]
    )


    # Add health analysis into main JSON
    data["health_analysis"] = report


    # Save updated weekly report
    with open("data/weekly_meal_plan.json", "w") as f:
        json.dump(
            data,
            f,
            indent=2
        )


    print("✅ Health analysis added to weekly_meal_plan.json")
