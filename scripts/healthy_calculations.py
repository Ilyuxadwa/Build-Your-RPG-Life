def bmi(weight: float, height: int, age: int, gender: str) -> dict:
    gender = gender.lower().strip()

    height_meters = height / 100.0
    raw_bmi = weight / (height_meters ** 2)
    
    if age < 25:
        min_normal, max_normal = 19.0, 24.0
    elif age <= 34:
        min_normal, max_normal = 20.0, 25.0
    elif age <= 44:
        min_normal, max_normal = 21.0, 26.0
    elif age <= 54:
        min_normal, max_normal = 22.0, 27.0
    elif age <= 64:
        min_normal, max_normal = 23.0, 28.0
    else:
        min_normal, max_normal = 24.0, 29.0

    if raw_bmi < min_normal:
        category = "Underweight"
    elif min_normal <= raw_bmi <= max_normal:
        category = "Normal Weight"
    elif max_normal < raw_bmi <= max_normal + 5.0:
        category = "Overweight"
    else:
        category = "Obese"

    base_ideal_bmi = 23.0 if gender == "male" else 21.0

    age_adjustment = 0
    if 25 <= age <= 34:
        age_adjustment = 1
    elif 35 <= age <= 44:
        age_adjustment = 2
    elif 45 <= age <= 54:
        age_adjustment = 3
    elif 55 <= age <= 64:
        age_adjustment = 4
    elif age > 64:
        age_adjustment = 5
        
    target_ideal_bmi = base_ideal_bmi + age_adjustment
    ideal_weight = target_ideal_bmi * (height_meters ** 2)
    
    weight_difference = weight - ideal_weight
    

    return {
        "bmi": round(raw_bmi, 1),
        "health_category": category,
        "normal_range": f"{min_normal} - {max_normal}",
        "ideal": round(ideal_weight, 1),
        "target": target_ideal_bmi,
        "difference": weight_difference
    }

def water(weight: float, age: int, gender: str) -> dict:
    base_ml_per_kg = 35.0 if gender == "male" else 30.0
    
    water_ml = weight * base_ml_per_kg
    
    if age < 18:
        water_ml += 200
    elif 18 <= age <= 55:
        pass
    elif 55 < age <= 65:
        water_ml *= 0.95
    else:
        water_ml *= 0.90

    final_water_ml = int(round(water_ml / 50.0) * 50)

    return final_water_ml
