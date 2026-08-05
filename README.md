# Medi Mind

Medi Mind is a full-stack educational disease prediction app built around the original Python symptom-classification model in this repository. The AI pipeline uses patient symptom text, TF-IDF vectorization, and a Multinomial Naive Bayes classifier to predict a likely disease category with confidence and care guidance.

> Medical disclaimer: Medi Mind is not a certified diagnostic tool and does not replace professional medical consultation.

## Features

- Modern responsive landing page with disease detection overview, benefits, FAQ, contact, navbar, and footer
- Detection page for symptom-based prediction
- Optional medical image preview for user context
- Confidence percentage, disease prediction, emergency level, doctor suggestion, remedies, diet guidance, and disclaimer
- Dashboard with model accuracy, dataset statistics, top diseases, and recent predictions
- About page with technology stack, AI model explanation, and placeholder team section
- FastAPI backend with clean model service and validation
- React + Vite frontend with reusable sections and accessible controls

## Tech Stack

| Layer | Technology |
| --- | --- |
| AI / ML | TF-IDF Vectorizer, Multinomial Naive Bayes, scikit-learn |
| Data | CSV dataset, pandas |
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Vite, lucide-react |
| Storage | In-memory prediction history for the current backend session |

## AI Model

The existing trained-at-runtime model is preserved:

1. Load `patient_symptoms_textual.csv`
2. Clean `patient_concern` and `diagnosis`
3. Split data with an 80/20 train-test split
4. Train a scikit-learn pipeline:
   - `TfidfVectorizer`
   - `MultinomialNB`
5. Return prediction and confidence using `predict` and `predict_proba`

The current repository does not include an image classification model. Image upload in the web UI is a preview/context feature only; disease prediction is based on symptom text.

## Folder Structure

```text
Medi_Mind/
  backend/
    app/
      __init__.py
      main.py
      model_service.py
      schemas.py
    requirements.txt
  frontend/
    src/
      services/
        api.js
      App.jsx
      main.jsx
      styles.css
    index.html
    package.json
  Advance_Disease_Detector_AI.py
  disease_deletctor_ai.py
  patient_symptoms_textual.csv
  README.md
```

## Installation

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/api/predict` | Predict disease from symptom text |
| GET | `/api/stats` | Return model accuracy, dataset stats, top diseases, and recent predictions |

Example prediction request:

```json
{
  "symptoms": "severe headache with nausea and sensitivity to light",
  "image_filename": null
}
```

## Screenshots

Add screenshots after running the app:

- `docs/screenshots/landing-page.png`
- `docs/screenshots/detection-page.png`
- `docs/screenshots/dashboard.png`
- `docs/screenshots/mobile-view.png`

## Deployment

### Backend

Deploy the FastAPI app to a Python-friendly host such as Render, Railway, Azure App Service, or a VPS.

Recommended command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

Build the React app:

```bash
cd frontend
npm run build
```

Deploy the generated `frontend/dist` folder to Vercel, Netlify, Cloudflare Pages, or any static hosting service.

Set the frontend environment variable if the backend is hosted elsewhere:

```text
VITE_API_BASE_URL=https://your-backend-url.example.com
```

## Original CLI Scripts

The original scripts are kept for reference and local CLI usage:

- `Advance_Disease_Detector_AI.py`
- `disease_deletctor_ai.py`

The web backend reuses the same dataset and model approach in `backend/app/model_service.py`.

## Author

Manav Parikh
