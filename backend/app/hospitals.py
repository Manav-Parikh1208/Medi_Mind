from urllib.parse import quote_plus

HOSPITAL_DATABASE = {
    "cardiac": [
        {
            "name": "Apollo Heart & Vascular Institute",
            "specialty": "Cardiology & Cardiac Surgery",
            "distance": "1.8 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7890",
            "address": "45 Healthcare Boulevard, Medical District",
            "services": ["24/7 Cardiac Emergency", "Cath Lab", "ICU & CCU", "ECG/ECHO Diagnostic"],
        },
        {
            "name": "Fortis Cardiac & Trauma Care Center",
            "specialty": "Emergency Cardiology & Vascular Care",
            "distance": "3.2 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7891",
            "address": "102 Central Avenue, Heart Care Wing",
            "services": ["Cardiac ICU", "Coronary Care", "Emergency Ambulance", "Angiography"],
        },
        {
            "name": "Max Super Speciality Heart Center",
            "specialty": "Cardiovascular Sciences & Critical Care",
            "distance": "4.5 km",
            "rating": 4.7,
            "emergency_24x7": True,
            "phone": "+1-800-432-7892",
            "address": "88 Wellness Park Road",
            "services": ["24/7 Chest Pain Unit", "Cardiac Surgery", "Non-Invasive Diagnostics"],
        },
        {
            "name": "Metro General & Cardiac Hospital",
            "specialty": "Internal Medicine & Heart Care",
            "distance": "5.1 km",
            "rating": 4.6,
            "emergency_24x7": True,
            "phone": "+1-800-432-7893",
            "address": "12 Station Road, Medical Enclave",
            "services": ["24/7 OPD & Emergency", "Cardiac Care Ward", "Pathology Lab"],
        },
    ],
    "neurology": [
        {
            "name": "City Neuro Care & Brain Institute",
            "specialty": "Neurology & Headache Clinic",
            "distance": "2.1 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7894",
            "address": "15 Neuro Science Drive",
            "services": ["Migraine & Headache Clinic", "24/7 Stroke Unit", "3T MRI & EEG Diagnostic"],
        },
        {
            "name": "Medanta Institute of Neurosciences",
            "specialty": "Neurology & Neurosurgery",
            "distance": "3.8 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7895",
            "address": "77 Knowledge Park Way",
            "services": ["Neuro ICU", "Comprehensive Pain Management", "Brain & Nerve Care"],
        },
        {
            "name": "Manipal Brain & Nerve Care Hospital",
            "specialty": "Clinical Neurology & Neuro-Pain",
            "distance": "4.2 km",
            "rating": 4.7,
            "emergency_24x7": False,
            "phone": "+1-800-432-7896",
            "address": "33 Hospital Road, West Wing",
            "services": ["Specialist OPD", "Nerve Conduction Study", "Infusion Therapy"],
        },
    ],
    "gastro": [
        {
            "name": "Global Institute of Gastroenterology",
            "specialty": "Gastroenterology & Liver Care",
            "distance": "1.5 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7897",
            "address": "50 Digestive Health Lane",
            "services": ["24/7 Emergency Endoscopy", "Acute Dehydration Unit", "Gastro ICU"],
        },
        {
            "name": "Apollo Digestive Care Hospital",
            "specialty": "Gastroenterology & Clinical Nutrition",
            "distance": "2.9 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7898",
            "address": "99 Clinical Parkway",
            "services": ["Emergency IV Rehydration", "Endoscopic Diagnostics", "Inpatient Care"],
        },
        {
            "name": "Sunshine Medical & Gastro Center",
            "specialty": "General Medicine & Gastroenterology",
            "distance": "4.0 km",
            "rating": 4.6,
            "emergency_24x7": True,
            "phone": "+1-800-432-7899",
            "address": "21 Market Road, Sector 4",
            "services": ["24/7 Pharmacy", "Stomach & Bowel Clinic", "Ultrasound Diagnostics"],
        },
    ],
    "pulmonology": [
        {
            "name": "National Chest & Respiratory Institute",
            "specialty": "Pulmonology & Respiratory Medicine",
            "distance": "2.3 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7900",
            "address": "64 Breath Care Avenue",
            "services": ["24/7 Oxygen & ICU", "Asthma & Allergy Clinic", "Nebulization Ward"],
        },
        {
            "name": "Fortis Pulmonary Care Hospital",
            "specialty": "Respiratory Medicine & Critical Care",
            "distance": "3.5 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7901",
            "address": "11 Green Valley Road",
            "services": ["Pneumonia Care Ward", "High-Flow Oxygen Unit", "Pulmonary Function Lab"],
        },
        {
            "name": "City General & Lung Care Hospital",
            "specialty": "General Medicine & Respiratory Care",
            "distance": "4.8 km",
            "rating": 4.7,
            "emergency_24x7": True,
            "phone": "+1-800-432-7902",
            "address": "309 Main Boulevard",
            "services": ["24/7 OPD & Emergency", "Chest X-Ray & CT", "Inhalation Therapy"],
        },
    ],
    "urology": [
        {
            "name": "Specialty Urology & Kidney Care Center",
            "specialty": "Urology & Nephrology",
            "distance": "2.0 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7903",
            "address": "82 Renal Care Boulevard",
            "services": ["24/7 Kidney Stone Emergency", "Laser Lithotripsy", "Dialysis Unit"],
        },
        {
            "name": "Apex Nephrology & Urinary Care Center",
            "specialty": "Nephrology & Urinary Sciences",
            "distance": "3.4 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7904",
            "address": "14 Medical Plaza, East Wing",
            "services": ["UTI Specialty Clinic", "Kidney Ultrasound", "Emergency Care"],
        },
        {
            "name": "Sunrise Urology Clinic & Hospital",
            "specialty": "General Urology & Internal Medicine",
            "distance": "5.0 km",
            "rating": 4.7,
            "emergency_24x7": False,
            "phone": "+1-800-432-7905",
            "address": "60 Station Square",
            "services": ["Specialist Consultation", "Diagnostic Pathology", "Day Care Procedures"],
        },
    ],
    "fever_infectious": [
        {
            "name": "St. Jude Multi-Specialty Fever Hospital",
            "specialty": "Infectious Diseases & Tropical Medicine",
            "distance": "1.9 km",
            "rating": 4.9,
            "emergency_24x7": True,
            "phone": "+1-800-432-7906",
            "address": "25 Cross Road, Fever Clinic Wing",
            "services": ["24/7 High-Tech Blood Lab", "Platelet Transfusion Unit", "Fever ICU"],
        },
        {
            "name": "Care Infectious Disease & Critical Care",
            "specialty": "Internal Medicine & Infection Care",
            "distance": "3.1 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7907",
            "address": "90 Sunrise Avenue",
            "services": ["Dengue & Malaria Isolation Ward", "24/7 Emergency", "Complete Diagnostic Lab"],
        },
        {
            "name": "Lifeline General & Emergency Hospital",
            "specialty": "General Medicine & Pediatric Care",
            "distance": "4.4 km",
            "rating": 4.7,
            "emergency_24x7": True,
            "phone": "+1-800-432-7908",
            "address": "108 Central Spine Road",
            "services": ["24/7 OPD", "IV Fluid Therapy", "Inpatient Care"],
        },
    ],
    "ortho": [
        {
            "name": "Bone & Joint Specialty Institute",
            "specialty": "Orthopedics & Rheumatology",
            "distance": "2.4 km",
            "rating": 4.9,
            "emergency_24x7": False,
            "phone": "+1-800-432-7909",
            "address": "78 Ortho Center Drive",
            "services": ["Arthritis & Joint Clinic", "Physiotherapy & Rehab", "Digital X-Ray"],
        },
        {
            "name": "Apollo Orthopedic & Spine Hospital",
            "specialty": "Advanced Orthopedics & Joint Care",
            "distance": "3.7 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7910",
            "address": "40 Health Expressway",
            "services": ["24/7 Emergency Care", "Joint Injections", "Diagnostic MRI"],
        },
        {
            "name": "City Rheumatology & Joint Care Center",
            "specialty": "Rheumatology & Autoimmune Care",
            "distance": "4.6 km",
            "rating": 4.7,
            "emergency_24x7": False,
            "phone": "+1-800-432-7911",
            "address": "19 Unity Street",
            "services": ["Specialist OPD", "Infusion Clinic", "Physical Therapy"],
        },
    ],
    "dermatology": [
        {
            "name": "Skin & Allergy Specialty Institute",
            "specialty": "Dermatology & Clinical Immunology",
            "distance": "1.6 km",
            "rating": 4.9,
            "emergency_24x7": False,
            "phone": "+1-800-432-7912",
            "address": "31 Dermatology Way",
            "services": ["Allergy Patch Testing", "Hives & Rash Treatment", "Dermato-Immunology"],
        },
        {
            "name": "Fortis Skin & Allergy Care Hospital",
            "specialty": "Dermatology & Emergency Medicine",
            "distance": "3.0 km",
            "rating": 4.8,
            "emergency_24x7": True,
            "phone": "+1-800-432-7913",
            "address": "85 Oak Tree Lane",
            "services": ["24/7 Emergency Care", "Severe Allergy Injections", "Inpatient Care"],
        },
        {
            "name": "Apex Multi-Specialty Clinic",
            "specialty": "General Medicine & Dermatology",
            "distance": "4.1 km",
            "rating": 4.7,
            "emergency_24x7": False,
            "phone": "+1-800-432-7914",
            "address": "14 Civic Center",
            "services": ["Specialist OPD", "24/7 Pharmacy", "Diagnostic Lab"],
        },
    ],
}


def get_hospital_recommendations(disease_name: str) -> list[dict]:
    disease_lower = disease_name.lower()

    if any(k in disease_lower for k in ["cardiac", "blood pressure", "hypertension", "heart"]):
        category = "cardiac"
    elif any(k in disease_lower for k in ["migraine", "headache", "brain", "stroke", "neuro"]):
        category = "neurology"
    elif any(k in disease_lower for k in ["food poisoning", "acidity", "gastroenteritis", "gerd", "stomach"]):
        category = "gastro"
    elif any(k in disease_lower for k in ["asthma", "pneumonia", "flu", "cold", "throat", "bronchitis", "lung"]):
        category = "pulmonology"
    elif any(k in disease_lower for k in ["uti", "kidney", "urinary", "renal"]):
        category = "urology"
    elif any(k in disease_lower for k in ["dengue", "malaria", "typhoid", "infection", "fever"]):
        category = "fever_infectious"
    elif any(k in disease_lower for k in ["arthritis", "joint", "rheumatoid", "bone"]):
        category = "ortho"
    elif any(k in disease_lower for k in ["allergy", "skin", "rash", "eczema"]):
        category = "dermatology"
    else:
        category = "fever_infectious"

    raw_hospitals = HOSPITAL_DATABASE.get(category, HOSPITAL_DATABASE["fever_infectious"])
    results = []

    for item in raw_hospitals:
        maps_query = quote_plus(f"{item['name']} {item['address']}")
        item_copy = dict(item)
        item_copy["map_url"] = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
        results.append(item_copy)

    return results
