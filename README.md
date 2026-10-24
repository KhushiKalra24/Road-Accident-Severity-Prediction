# Road Accident Severity Prediction Website

This folder contains a Flask website assembled around the two files supplied:
- `app.py` — the original Flask backend (copied without changing its prediction logic)
- `road_accident_severity_model.pkl` — the supplied trained model

Frontend files added:
- `index.html`
- `style.css`
- `script.js`

## Run on Windows

Use Python 3.12 for compatibility with the model's stated scikit-learn version.

1. Extract this folder.
2. Open the folder in VS Code.
3. Open the terminal in this folder and run:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

4. Open http://127.0.0.1:5000 in your browser.

## Important notes

- This is a local Flask development server, suitable for testing and demos, not public production hosting.
- The backend accepts 9 fields from the form and fills the other 22 of its 31 model features with the default values already present in the supplied `app.py`.
- Those defaults are assumptions, not information collected from the user, and can affect predictions.
- The supplied backend uses `predict_proba()`. If the model does not support it, prediction handling will return an error.
- The website is an educational demonstration only, not a real-world safety or emergency decision tool.
- If the model fails to load, verify the Python and scikit-learn versions.
