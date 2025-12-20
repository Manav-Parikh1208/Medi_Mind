Advanced Disease Detector AI

AI Medical Chatbot + Analytics Dashboard

Project Overview

The Advanced Disease Detector AI is a Python-based intelligent medical assistant that analyzes patient symptom descriptions and predicts possible diseases using Machine Learning.
It also provides emergency level detection, home remedies, diet recommendations, doctor suggestions, and interactive visual analytics.

Note: This project is for educational purposes only and does not replace professional medical consultation.
Key Features
->Disease Prediction using TF-IDF + Naive Bayes
->Data Visualizations
--->Disease Frequency Bar Chart
--->Disease Distribution Pie Chart
--->Symptoms WordCloud

Confidence Score for each prediction
Emergency Level Detection (LOW / MEDIUM / HIGH)
Doctor Specialization Suggestion
Diet Recommendations
Home Remedies
Interactive AI Medical Chatbot

Technologies Used
-----------------
Python 3
Pandas – Data handling
Matplotlib – Visualizations
WordCloud – Text analytics
Scikit-learn – Machine Learning
TF-IDF Vectorizer
Multinomial Naive Bayes

Project Structure
-----------------
Advanced_Disease_Detector_AI/
│
├── Advance_Disease_Detector_AI.py
├── patient_symptoms_textual.csv
├── README.md

Dataset Details
---------------
The dataset file patient_symptoms_textual.csv must contain:

Column Name	Description
patient_concern	Textual description of symptoms
diagnosis	Corresponding disease label


Missing values are automatically cleaned.
Machine Learning Model

Input: Patient symptom text
Vectorization: TF-IDF
Classifier: Multinomial Naive Bayes
Train-Test Split: 80% / 20%

Output: Disease prediction + confidence score

How to Run the Project
Install Required Libraries
pip install pandas matplotlib wordcloud scikit-learn

Run the Program
python Advance_Disease_Detector_AI.py

Chatbot Usage

After execution, the chatbot will prompt:

Describe your symptoms (or type exit):

Example Input:
i have severe headache and nausea

Example Output:

Predicted Diagnosis

Confidence Score

Emergency Level

Home Remedies

Doctor Recommendation

Diet Plan

Type exit to quit.

Disclaimer

This AI system:

Is NOT a certified medical diagnostic tool
Does NOT provide prescriptions
Is meant for learning, demonstration, and academic projects

Always consult a licensed medical professional for health issues.

Ideal For
--------
Final Year Projects

AI / ML Mini Projects

Data Science Demonstrations

Healthcare AI Prototypes

Portfolio & GitHub Showcase

Author
------
Palak Gandhi
Advanced AI & Data Science Project