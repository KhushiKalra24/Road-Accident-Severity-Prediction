
from pathlib import Path
import warnings
import joblib
import pandas as pd
from flask import Flask, jsonify, request, render_template

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "road_accident_severity_model.pkl"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static"
)

FEATURES = [
    "Time", "Day_of_week", "Age_band_of_driver", "Sex_of_driver",
    "Educational_level", "Vehicle_driver_relation", "Driving_experience",
    "Type_of_vehicle", "Owner_of_vehicle", "Service_year_of_vehicle",
    "Defect_of_vehicle", "Area_accident_occured", "Lanes_or_Medians",
    "Road_allignment", "Types_of_Junction", "Road_surface_type",
    "Road_surface_conditions", "Light_conditions", "Weather_conditions",
    "Type_of_collision", "Number_of_vehicles_involved", "Number_of_casualties",
    "Vehicle_movement", "Casualty_class", "Sex_of_casualty",
    "Age_band_of_casualty", "Casualty_severity", "Work_of_casuality",
    "Fitness_of_casuality", "Pedestrian_movement", "Cause_of_accident"
]

DEFAULTS = {
    "Time": "17:30",
    "Day_of_week": "Monday",
    "Sex_of_driver": "Male",
    "Educational_level": "High school",
    "Vehicle_driver_relation": "Owner",
    "Owner_of_vehicle": "Owner",
    "Service_year_of_vehicle": "2-5yrs",
    "Defect_of_vehicle": "No defect",
    "Area_accident_occured": "Other",
    "Lanes_or_Medians": "Two-way",
    "Road_allignment": "Tangent road with flat terrain",
    "Types_of_Junction": "Y Shape",
    "Road_surface_type": "Asphalt roads",
    "Type_of_collision": "Vehicle with vehicle collision",
    "Vehicle_movement": "Going straight",
    "Casualty_class": "Driver or rider",
    "Sex_of_casualty": "Male",
    "Age_band_of_casualty": "18-30",
    "Casualty_severity": "3",
    "Work_of_casuality": "Employee",
    "Fitness_of_casuality": "Normal",
    "Pedestrian_movement": "Not a Pedestrian",
}

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    model = None
    MODEL_LOAD_ERROR = str(exc)
else:
    MODEL_LOAD_ERROR = None


def make_model_row(data):
    row = DEFAULTS.copy()

    row.update({
        "Age_band_of_driver": data["Age_band_of_driver"],
        "Driving_experience": data["Driving_experience"],
        "Type_of_vehicle": data["Type_of_vehicle"],
        "Road_surface_conditions": data["Road_surface_conditions"],
        "Light_conditions": data["Light_conditions"],
        "Weather_conditions": data["Weather_conditions"],
        "Number_of_vehicles_involved": int(data["Number_of_vehicles_involved"]),
        "Number_of_casualties": int(data["Number_of_casualties"]),
        "Cause_of_accident": data["Cause_of_accident"],
    })

    return pd.DataFrame(
        [[row[name] for name in FEATURES]],
        columns=FEATURES
    )


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/predict")
def predict():
    if model is None:
        return jsonify({
            "error": "Model load failed. Install the exact requirements from requirements.txt. Details: " + str(MODEL_LOAD_ERROR)
        }), 500

    data = request.get_json(silent=True) or {}

    required = [
        "Age_band_of_driver",
        "Driving_experience",
        "Type_of_vehicle",
        "Road_surface_conditions",
        "Light_conditions",
        "Weather_conditions",
        "Number_of_vehicles_involved",
        "Number_of_casualties",
        "Cause_of_accident"
    ]

    missing = [
        name for name in required
        if name not in data or data[name] in (None, "")
    ]

    if missing:
        return jsonify({"error": "Please complete all fields."}), 400

    try:
        row = make_model_row(data)

        predicted_label = str(model.predict(row)[0])
        probabilities = model.predict_proba(row)[0]
        classes = [str(c) for c in model.classes_]

        display_names = {
            "Fatal injury": "Fatal Accident",
            "Serious Injury": "Serious Injury",
            "Slight Injury": "Slight Injury",
        }

        prediction = display_names.get(predicted_label, predicted_label)

        probs = [
            {
                "label": display_names.get(label, label),
                "percentage": round(float(prob) * 100, 2)
            }
            for label, prob in zip(classes, probabilities)
        ]

        return jsonify({
            "prediction": prediction,
            "model_label": predicted_label,
            "probabilities": probs,
            "note": "Educational prediction only. Not for emergency or real-world safety decisions."
        })

    except Exception as exc:
        return jsonify({
            "error": "Prediction failed: " + str(exc)
        }), 500


if __name__ == "__main__":
    if model is None:
        print("WARNING: Model could not be loaded:", MODEL_LOAD_ERROR)
        print("Install requirements.txt in a clean environment and try again.")

    app.run(host="127.0.0.1", port=5000, debug=False)
