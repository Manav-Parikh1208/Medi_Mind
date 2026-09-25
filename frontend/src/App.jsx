import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Brain,
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  Heart,
  HeartPulse,
  Hospital,
  Info,
  Loader2,
  MapPin,
  Menu,
  Microscope,
  PhoneCall,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Star,
  Stethoscope,
  ThumbsUp,
  Upload,
  UserCheck,
  X,
} from 'lucide-react';
import { getStats, getVitals, predictDisease, submitFeedback } from './services/api';

const initialQuestionnaire = {
  patientName: '',
  age: '',
  sex: '',
  symptomGroup: '',
  symptomDuration: '',
  severity: '',
  symptoms: '',
  preExistingConditions: [],
  heartRate: '',
  averageHeartRate: '',
};

const navItems = [
  { id: 'home', label: 'Home' },
  { id: 'detect', label: 'Symptom & Vital Checker' },
  { id: 'hospitals', label: 'Hospitals' },
  { id: 'survey', label: 'Model Feedback' },
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'about', label: 'About' },
  { id: 'contact', label: 'Contact' },
];

const faqs = [
  {
    question: 'How does live heart rate monitoring affect disease prediction?',
    answer: 'Live heart rate and average BPM are streamed from the MAX30102 / ESP32 sensor. Abnormally high (tachycardia >100 BPM) or low (<60 BPM) heart rates combined with symptoms like chest pain escalate emergency level warnings and provide vital triage guidance.',
  },
  {
    question: 'Does Medi Mind diagnose medical conditions?',
    answer: 'No. Medi Mind provides educational AI predictions, vital triage assessments, and differential diagnoses. Always review results with a qualified clinician.',
  },
  {
    question: 'How does nearest hospital recommendation work?',
    answer: 'Based on the predicted disease and medical specialty (e.g. Cardiology for heart issues, Neurology for migraines, Pulmonology for asthma/pneumonia), Medi Mind suggests specialized 24/7 hospital centers with location distance, ratings, and direct navigation links.',
  },
  {
    question: 'How does the accuracy survey and feedback retrain work?',
    answer: 'If the AI prediction is incorrect or if you select an alternative differential diagnosis, submitting your feedback automatically appends your verified case to the dataset and retrains the AI model live, continuously boosting prediction accuracy.',
  },
];

const features = [
  { icon: HeartPulse, title: 'Live Heart Rate & Vitals Triage', text: 'Streams real-time BPM and rolling average heart rate from MAX30102 to assess physiological risk.' },
  { icon: Brain, title: 'AI Symptom Intelligence', text: 'Predicts high-accuracy main disease categories and multi-class differential diagnoses from natural text.' },
  { icon: Hospital, title: 'Nearest Specialty Hospitals', text: 'Recommends 3-4 top nearby hospitals, emergency care centers, and specialty clinics tailored to your diagnosis.' },
  { icon: RefreshCw, title: 'Interactive Accuracy Feedback', text: 'Enables users to submit survey corrections that dynamically update the dataset and retrain the AI model in real time.' },
];

const symptomGroups = [
  'Fever, chills, body ache, or weakness',
  'Headache, temple pain, or migraine',
  'Cough, chest congestion, or breathing difficulty',
  'Stomach pain, acidity, nausea, or vomiting',
  'Urinary burning, lower pelvic or flank pain',
  'Chest pain, tightness, or blood pressure issue',
  'Joint pain, swelling, or knee stiffness',
  'Skin allergy, rash, hives, or itching',
];

const preExistingOptions = [
  'Diabetes',
  'Asthma',
  'Blood pressure issue',
  'Cardiac issue',
  'Arthritis',
  'Allergy',
  'None',
];

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState('');
  const [vitals, setVitals] = useState({
    state: 'disconnected',
    message: 'ESP32 is unavailable on COM13. Connect it, then close Arduino Serial Monitor or any other serial app.',
    heart_rate: null,
    average_heart_rate: null,
  });
  const [questionnaire, setQuestionnaire] = useState(initialQuestionnaire);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState('');

  // Survey Feedback State
  const [feedbackSelected, setFeedbackSelected] = useState('');
  const [customDisease, setCustomDisease] = useState('');
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((error) => setStatsError(error.message));

    const pollVitals = () => {
      getVitals()
        .then((data) => {
          setVitals(data);
          if (data.heart_rate) {
            setQuestionnaire((curr) => ({
              ...curr,
              heartRate: curr.heartRate || String(Math.round(data.heart_rate)),
              averageHeartRate: curr.averageHeartRate || (data.average_heart_rate ? String(data.average_heart_rate) : ''),
            }));
          }
        })
        .catch(() => {});
    };

    pollVitals();
    const interval = setInterval(pollVitals, 2500);
    return () => clearInterval(interval);
  }, []);

  const confidenceStyle = useMemo(() => {
    const value = prediction?.confidence || 0;
    return { '--confidence': `${Math.min(value, 100)}%` };
  }, [prediction]);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setMenuOpen(false);
  };

  const updateQuestion = (field, value) => {
    setQuestionnaire((current) => ({ ...current, [field]: value }));
  };

  const toggleCondition = (condition) => {
    setQuestionnaire((current) => {
      if (condition === 'None') {
        return { ...current, preExistingConditions: current.preExistingConditions.includes('None') ? [] : ['None'] };
      }

      const withoutNone = current.preExistingConditions.filter((item) => item !== 'None');
      const next = withoutNone.includes(condition)
        ? withoutNone.filter((item) => item !== condition)
        : [...withoutNone, condition];

      return { ...current, preExistingConditions: next };
    });
  };

  const handlePredict = async (event) => {
    event.preventDefault();
    setPrediction(null);
    setNotice('');
    setFeedbackMsg(null);
    setFeedbackSelected('');
    setCustomDisease('');

    if (!questionnaire.patientName.trim()) {
      setNotice('Please enter the patient name.');
      return;
    }
    if (!questionnaire.age || Number(questionnaire.age) < 1 || Number(questionnaire.age) > 120) {
      setNotice('Please enter a valid age between 1 and 120.');
      return;
    }
    if (!questionnaire.symptomGroup) {
      setNotice('Please select the closest symptom category.');
      return;
    }
    if (questionnaire.symptoms.trim().split(/\s+/).length < 3) {
      setNotice('Please describe the symptoms in at least three words.');
      return;
    }

    setLoading(true);
    try {
      const hrVal = questionnaire.heartRate ? Number(questionnaire.heartRate) : vitals.heart_rate;
      const avgHrVal = questionnaire.averageHeartRate ? Number(questionnaire.averageHeartRate) : vitals.average_heart_rate;

      const result = await predictDisease({
        symptoms: questionnaire.symptoms,
        patient_name: questionnaire.patientName,
        age: Number(questionnaire.age),
        sex: questionnaire.sex || null,
        symptom_group: questionnaire.symptomGroup,
        symptom_duration: questionnaire.symptomDuration || null,
        severity: questionnaire.severity || null,
        pre_existing_conditions: questionnaire.preExistingConditions,
        heart_rate: hrVal,
        average_heart_rate: avgHrVal,
        image_filename: null,
      });
      setPrediction(result);
      setFeedbackSelected(result.predicted_disease);
      const nextStats = await getStats();
      setStats(nextStats);

      setTimeout(() => {
        document.getElementById('result-anchor')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (error) {
      setNotice(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (event) => {
    event.preventDefault();
    if (!prediction) return;

    const chosenDisease = feedbackSelected === 'other' ? customDisease.trim() : feedbackSelected;
    if (!chosenDisease) {
      setFeedbackMsg({ type: 'error', text: 'Please select or enter the correct disease name.' });
      return;
    }

    setFeedbackSubmitting(true);
    setFeedbackMsg(null);

    try {
      const res = await submitFeedback({
        prediction_id: prediction.id,
        symptoms: prediction.symptoms,
        predicted_disease: prediction.predicted_disease,
        user_corrected_disease: chosenDisease,
        is_correct: chosenDisease.toLowerCase() === prediction.predicted_disease.toLowerCase(),
      });

      setFeedbackMsg({ type: 'success', text: res.message });
      const nextStats = await getStats();
      setStats(nextStats);
    } catch (err) {
      setFeedbackMsg({ type: 'error', text: err.message });
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  return (
    <div className="app">
      <header className="site-header">
        <button className="brand" onClick={() => scrollTo('home')} aria-label="Go to home">
          <span className="brand-mark"><HeartPulse size={22} /></span>
          <span className="brand-text">Medi Mind AI</span>
        </button>
        <nav className={menuOpen ? 'nav nav-open' : 'nav'} aria-label="Main navigation">
          {navItems.map((item) => (
            <button key={item.id} onClick={() => scrollTo(item.id)}>
              {item.label}
            </button>
          ))}
        </nav>
        <button className="icon-button menu-button" onClick={() => setMenuOpen((open) => !open)} aria-label="Toggle menu">
          {menuOpen ? <X /> : <Menu />}
        </button>
      </header>

      <main>
        {/* HERO SECTION */}
        <section className="hero section" id="home">
          <div className="hero-copy">
            <span className="eyebrow"><Sparkles size={16} /> Advanced AI Medical Assistant</span>
            <h1>Live Heart Rate Tracking, AI Symptom Diagnosis & Nearby Hospitals</h1>
            <p>
              Medi Mind combines live MAX30102 pulse monitoring, rolling average heart rate calculation, high-accuracy disease prediction,
              nearest 24/7 hospital routing, and live model retraining feedback.
            </p>
            <div className="hero-actions">
              <button className="primary-button" onClick={() => scrollTo('detect')}>
                Check Symptoms & Vitals <ArrowRight size={18} />
              </button>
              <button className="secondary-button" onClick={() => scrollTo('dashboard')}>View Live Analytics</button>
            </div>
          </div>

          <div className="hero-visual" aria-label="Medical analytics illustration">
            {/* LIVE HEART RATE CARD */}
            <div className={`vitals-card vitals-${vitals.state}`}>
              <div className="vitals-icon"><Heart size={24} className={vitals.heart_rate ? 'pulse-heart' : ''} /></div>
              <div className="vitals-copy">
                <span className="vitals-label">LIVE SENSOR FEED (COM13)</span>
                <strong>{vitals.heart_rate ? `${Math.round(vitals.heart_rate)} BPM` : 'No vital'}</strong>
                <p>{vitals.message}</p>
              </div>
              <div className="vitals-meta">
                <span>{vitals.average_heart_rate ? `AVG: ${vitals.average_heart_rate} BPM` : 'AVERAGE BPM'}</span>
                <i />
              </div>
            </div>

            <div className="pulse-card">
              <Activity size={28} />
              <span>Model Accuracy</span>
              <strong>{stats ? `${stats.accuracy}%` : 'Loading'}</strong>
            </div>

            <div className="hospital-card-preview">
              <Hospital size={22} />
              <span>Recommended Specialty Hospitals & ER</span>
            </div>

            <div className="diagnosis-chip"><Stethoscope size={18} /> Vital Triage & Symptom AI</div>
          </div>
        </section>

        {/* OVERVIEW SECTION */}
        <section className="section overview">
          <div className="section-heading">
            <span className="eyebrow"><Microscope size={16} /> Key Capabilities</span>
            <h2>Comprehensive Medical AI & Vital Platform</h2>
            <p>
              Designed for live physiological monitoring, precision diagnostic assistance, hospital location routing, and interactive model retrain feedback.
            </p>
          </div>
          <div className="feature-grid">
            {features.map(({ icon: Icon, title, text }) => (
              <article className="feature-card" key={title}>
                <div className="feature-icon"><Icon size={24} /></div>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        {/* DETECTOR & VITALS SECTION */}
        <section className="section detector" id="detect">
          <div className="section-heading">
            <span className="eyebrow"><Upload size={16} /> AI Symptom & Vital Checker</span>
            <h2>Patient Questionnaire & Live Heart Rate Analysis</h2>
            <p>Stream live heart rate from MAX30102 sensor, describe symptoms in natural language, and generate diagnostic predictions.</p>
          </div>

          <div className="detector-layout">
            <form className="detector-form" onSubmit={handlePredict}>
              {/* LIVE VITALS SENSOR BANNER */}
              <div className={`vitals-card vitals-${vitals.state}`}>
                <div className="vitals-icon"><Heart size={24} className={vitals.heart_rate ? 'pulse-heart' : ''} /></div>
                <div className="vitals-copy">
                  <span className="vitals-label">LIVE MAX30102 HARDWARE FEED</span>
                  <strong>{vitals.heart_rate ? `${Math.round(vitals.heart_rate)} BPM` : 'No Live Pulse'}</strong>
                  <p>{vitals.message}</p>
                </div>
                <div className="vitals-meta">
                  <span>{vitals.average_heart_rate ? `AVG RESTING: ${vitals.average_heart_rate} BPM` : 'AVERAGE BPM'}</span>
                  <i />
                </div>
              </div>

              <div className="form-grid">
                <div className="field">
                  <label htmlFor="patientName">Patient Name *</label>
                  <input
                    id="patientName"
                    value={questionnaire.patientName}
                    onChange={(event) => updateQuestion('patientName', event.target.value)}
                    placeholder="e.g. John Doe"
                  />
                </div>
                <div className="field">
                  <label htmlFor="age">Age *</label>
                  <input
                    id="age"
                    min="1"
                    max="120"
                    type="number"
                    value={questionnaire.age}
                    onChange={(event) => updateQuestion('age', event.target.value)}
                    placeholder="Age"
                  />
                </div>
              </div>

              <div className="form-grid">
                <div className="field heart-rate-field">
                  <div className="field-label-row">
                    <label htmlFor="heartRate">Current Heart Rate (BPM)</label>
                    {vitals.heart_rate ? <span className="live-tag">LIVE SENSOR</span> : <span className="saved-tag">MANUAL / OFF</span>}
                  </div>
                  <input
                    id="heartRate"
                    type="number"
                    value={questionnaire.heartRate}
                    onChange={(event) => updateQuestion('heartRate', event.target.value)}
                    placeholder={vitals.heart_rate ? `${Math.round(vitals.heart_rate)} BPM (Live)` : 'e.g. 75'}
                  />
                  <small>Auto-filled from ESP32 MAX30102 stream or manual entry.</small>
                </div>
                <div className="field">
                  <label htmlFor="averageHeartRate">Average Resting Pulse (BPM)</label>
                  <input
                    id="averageHeartRate"
                    type="number"
                    value={questionnaire.averageHeartRate}
                    onChange={(event) => updateQuestion('averageHeartRate', event.target.value)}
                    placeholder={vitals.average_heart_rate ? `${vitals.average_heart_rate} BPM (Avg)` : 'e.g. 72'}
                  />
                </div>
              </div>

              <div className="form-grid">
                <div className="field">
                  <label htmlFor="sex">Sex</label>
                  <select id="sex" value={questionnaire.sex} onChange={(event) => updateQuestion('sex', event.target.value)}>
                    <option value="">Select Sex</option>
                    <option>Female</option>
                    <option>Male</option>
                    <option>Other</option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="severity">Symptom Severity</label>
                  <select id="severity" value={questionnaire.severity} onChange={(event) => updateQuestion('severity', event.target.value)}>
                    <option value="">Select Severity</option>
                    <option>Mild</option>
                    <option>Moderate</option>
                    <option>Severe</option>
                  </select>
                </div>
              </div>

              <div className="field">
                <label htmlFor="symptomGroup">Closest Symptom Category *</label>
                <select
                  id="symptomGroup"
                  value={questionnaire.symptomGroup}
                  onChange={(event) => updateQuestion('symptomGroup', event.target.value)}
                >
                  <option value="">Choose a Category</option>
                  {symptomGroups.map((group) => <option key={group}>{group}</option>)}
                </select>
              </div>

              <div className="field">
                <label htmlFor="duration">Symptom Duration</label>
                <select
                  id="duration"
                  value={questionnaire.symptomDuration}
                  onChange={(event) => updateQuestion('symptomDuration', event.target.value)}
                >
                  <option value="">Select Duration</option>
                  <option>Today</option>
                  <option>1-2 days</option>
                  <option>3-7 days</option>
                  <option>More than a week</option>
                </select>
              </div>

              <div className="field">
                <label>Pre-existing Conditions</label>
                <div className="condition-grid">
                  {preExistingOptions.map((condition) => (
                    <button
                      className={questionnaire.preExistingConditions.includes(condition) ? 'condition selected' : 'condition'}
                      key={condition}
                      onClick={() => toggleCondition(condition)}
                      type="button"
                    >
                      {condition}
                    </button>
                  ))}
                </div>
              </div>

              <div className="field">
                <label htmlFor="symptoms">Describe Current Symptoms in Detail *</label>
                <textarea
                  id="symptoms"
                  value={questionnaire.symptoms}
                  onChange={(event) => updateQuestion('symptoms', event.target.value)}
                  placeholder="e.g. Sharp chest pain, shortness of breath, heaviness in chest with elevated pulse for 2 hours"
                  rows={4}
                />
              </div>

              {notice && <p className="notice error">{notice}</p>}

              <button className="primary-button full" disabled={loading} type="submit">
                {loading ? <Loader2 className="spin" size={18} /> : <Brain size={18} />}
                {loading ? 'Analyzing Symptoms & Vitals...' : 'Analyze Symptoms, Vitals & Find Hospitals'}
              </button>
            </form>

            <aside className="result-panel" id="result-anchor">
              {prediction ? (
                <div className="result-content">
                  {/* LIVE VITAL TRIAGE CARD */}
                  <section className={`vital-triage triage-${prediction.vital_triage_level.toLowerCase()}`}>
                    <span>Vital Triage Control</span>
                    <h3>{prediction.vital_triage_title}</h3>
                    <p>{prediction.vital_triage_message}</p>
                    <strong className="care-action">{prediction.primary_assessment}</strong>
                    <p className="care-copy">{prediction.care_action}</p>
                  </section>

                  <div className="result-header">
                    <span>
                      {prediction.symptom_result_is_secondary
                        ? 'Secondary symptom-pattern context for '
                        : 'Symptom-pattern result for '}
                      <strong>{questionnaire.patientName}</strong>
                    </span>
                    <h3 className="primary-disease">{prediction.predicted_disease}</h3>
                  </div>

                  <div className="patient-summary">
                    <span>{questionnaire.age} yrs</span>
                    {questionnaire.sex && <span>{questionnaire.sex}</span>}
                    {questionnaire.symptomGroup && <span>{questionnaire.symptomGroup}</span>}
                  </div>

                  <div className="confidence-meter">
                    <div className="confidence-label">
                      <span>Symptom-Pattern Confidence</span>
                      <strong>{prediction.confidence}%</strong>
                    </div>
                    <div className="confidence-track">
                      <div className="confidence-bar" style={{ width: `${prediction.confidence}%` }} />
                    </div>
                  </div>

                  <div className={`emergency-badge emergency-${prediction.emergency_level.toLowerCase()}`}>
                    <AlertTriangle size={16} />
                    <span>{prediction.emergency_level} EMERGENCY LEVEL</span>
                  </div>

                  <p className="explanation-text">{prediction.explanation}</p>

                  <div className="result-details">
                    <div className="detail-item">
                      <span className="detail-title"><HeartPulse size={16} /> Live Vital</span>
                      <p className="detail-value">{prediction.vital_summary || 'Heart-rate data unavailable.'}</p>
                    </div>

                    <div className="detail-item">
                      <span className="detail-title"><Stethoscope size={16} /> Doctor Specialist</span>
                      <p className="detail-value highlight">{prediction.doctor_recommendation}</p>
                    </div>

                    <div className="detail-item">
                      <span className="detail-title"><CheckCircle2 size={16} /> Home Care & Remedies</span>
                      <ul className="bullet-list">
                        {prediction.remedies.map((rem, i) => <li key={i}>{rem}</li>)}
                      </ul>
                    </div>

                    {prediction.diet_plan && (
                      <div className="detail-item">
                        <span className="detail-title"><Sparkles size={16} /> Diet Guidance</span>
                        <div className="diet-split">
                          <div>
                            <strong className="good">Recommended:</strong>
                            <p>{prediction.diet_plan.recommended.join(', ')}</p>
                          </div>
                          <div>
                            <strong className="bad">Avoid:</strong>
                            <p>{prediction.diet_plan.avoid.join(', ')}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="detail-item disclaimer-box">
                      <span className="detail-title"><Info size={16} /> Disclaimer</span>
                      <p>{prediction.disclaimer}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <Stethoscope size={48} />
                  <h3>Your AI Diagnostic Report Will Appear Here</h3>
                  <p>Enter patient symptoms and live heart rate to generate vital triage, disease prediction, nearest hospitals, and survey options.</p>
                </div>
              )}
            </aside>
          </div>
        </section>

        {/* NEAREST HOSPITALS SECTION */}
        {prediction && prediction.hospital_recommendations?.length > 0 && (
          <section className="section hospitals-section" id="hospitals">
            <div className="section-heading">
              <span className="eyebrow"><Hospital size={16} /> Emergency & Medical Routing</span>
              <h2>Nearest Recommended Hospitals for {prediction.predicted_disease}</h2>
              <p>Specialized healthcare centers equipped to treat this condition with 24/7 emergency facilities and specialist doctors.</p>
            </div>

            <div className="hospitals-grid">
              {prediction.hospital_recommendations.map((hosp, idx) => (
                <article className="hospital-card" key={idx}>
                  <div className="hospital-header">
                    <div className="hospital-title-wrap">
                      <span className="hospital-rank">#{idx + 1} Hospital Recommendation</span>
                      <h3>{hosp.name}</h3>
                      <span className="hospital-specialty">{hosp.specialty}</span>
                    </div>
                    <div className="hospital-rating">
                      <Star size={16} fill="#eab308" color="#eab308" />
                      <span>{hosp.rating}</span>
                    </div>
                  </div>

                  <div className="hospital-meta">
                    <span className="meta-badge distance">
                      <MapPin size={14} /> {hosp.distance} away
                    </span>
                    {hosp.emergency_24x7 && (
                      <span className="meta-badge emergency-247">
                        <AlertTriangle size={14} /> 24/7 Emergency & ICU
                      </span>
                    )}
                  </div>

                  <p className="hospital-address">{hosp.address}</p>

                  <div className="hospital-services">
                    <strong>Key Facilities:</strong>
                    <div className="services-chips">
                      {hosp.services.map((srv, sIdx) => (
                        <span key={sIdx} className="service-chip">{srv}</span>
                      ))}
                    </div>
                  </div>

                  <div className="hospital-actions">
                    <a className="phone-button" href={`tel:${hosp.phone}`}>
                      <PhoneCall size={16} /> {hosp.phone}
                    </a>
                    <a className="maps-button" href={hosp.map_url} target="_blank" rel="noopener noreferrer">
                      Get Directions <ExternalLink size={14} />
                    </a>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* SURVEY & ALTERNATIVE DIFFERENTIAL DIAGNOSIS SECTION */}
        {prediction && (
          <section className="section survey-section" id="survey">
            <div className="section-heading">
              <span className="eyebrow"><RefreshCw size={16} /> Dynamic Model Accuracy Survey</span>
              <h2>Differential Diagnoses & Accuracy Feedback</h2>
              <p>
                Was this prediction accurate? If not, select the actual disease from the differential options below to immediately retrain the AI model.
              </p>
            </div>

            <div className="survey-container">
              <div className="survey-card">
                <h3>1. Alternative Differential Diagnoses</h3>
                <p>The AI model identified these alternative potential matches based on your symptom description:</p>
                <div className="alternatives-grid">
                  <div className="alt-item main-alt">
                    <span className="alt-name">{prediction.predicted_disease} (Primary Match)</span>
                    <span className="alt-prob">{prediction.confidence}%</span>
                  </div>
                  {prediction.alternative_diseases.map((alt, aIdx) => (
                    <div className="alt-item" key={aIdx}>
                      <span className="alt-name">{alt.name}</span>
                      <span className="alt-prob">{alt.confidence}%</span>
                    </div>
                  ))}
                </div>

                <form className="survey-form" onSubmit={handleFeedbackSubmit}>
                  <h3>2. Is the main prediction accurate?</h3>
                  <div className="survey-options">
                    <label className="survey-radio">
                      <input
                        type="radio"
                        name="diseaseChoice"
                        value={prediction.predicted_disease}
                        checked={feedbackSelected === prediction.predicted_disease}
                        onChange={() => setFeedbackSelected(prediction.predicted_disease)}
                      />
                      <span><strong>Yes, correct:</strong> {prediction.predicted_disease} ({prediction.confidence}%)</span>
                    </label>

                    {prediction.alternative_diseases.map((alt) => (
                      <label className="survey-radio" key={alt.name}>
                        <input
                          type="radio"
                          name="diseaseChoice"
                          value={alt.name}
                          checked={feedbackSelected === alt.name}
                          onChange={() => setFeedbackSelected(alt.name)}
                        />
                        <span><strong>No, it should be:</strong> {alt.name} ({alt.confidence}%)</span>
                      </label>
                    ))}

                    <label className="survey-radio">
                      <input
                        type="radio"
                        name="diseaseChoice"
                        value="other"
                        checked={feedbackSelected === 'other'}
                        onChange={() => setFeedbackSelected('other')}
                      />
                      <span><strong>Other Disease (Select or type below)</strong></span>
                    </label>
                  </div>

                  {feedbackSelected === 'other' && (
                    <div className="other-select-box">
                      <label htmlFor="customDiseaseSelect">Select or Enter Disease Name:</label>
                      <select
                        id="customDiseaseSelect"
                        value={customDisease}
                        onChange={(e) => setCustomDisease(e.target.value)}
                      >
                        <option value="">Select from Dataset Diseases</option>
                        {(stats?.available_diseases || []).map((d) => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                      <input
                        type="text"
                        placeholder="Or type custom disease name"
                        value={customDisease}
                        onChange={(e) => setCustomDisease(e.target.value)}
                      />
                    </div>
                  )}

                  {feedbackMsg && (
                    <div className={`feedback-alert ${feedbackMsg.type}`}>
                      {feedbackMsg.type === 'success' ? <ThumbsUp size={18} /> : <AlertTriangle size={18} />}
                      <span>{feedbackMsg.text}</span>
                    </div>
                  )}

                  <button className="primary-button submit-feedback" disabled={feedbackSubmitting} type="submit">
                    {feedbackSubmitting ? <Loader2 className="spin" size={18} /> : <UserCheck size={18} />}
                    {feedbackSubmitting ? 'Submitting & Retraining Model...' : 'Submit Feedback & Retrain Model'}
                  </button>
                </form>
              </div>
            </div>
          </section>
        )}

        {/* DASHBOARD SECTION */}
        <section className="section dashboard" id="dashboard">
          <div className="section-heading">
            <span className="eyebrow"><BarChart3 size={16} /> Live Dashboard</span>
            <h2>Model Metrics & Training Statistics</h2>
          </div>
          {statsError && <p className="notice error">{statsError}</p>}
          <div className="stats-grid">
            <div className="stat"><span>Total Dataset Records</span><strong>{stats?.total_records ?? '--'}</strong></div>
            <div className="stat"><span>Tracked Disease Classes</span><strong>{stats?.total_diseases ?? '--'}</strong></div>
            <div className="stat"><span>Live Model Accuracy</span><strong>{stats ? `${stats.accuracy}%` : '--'}</strong></div>
          </div>
          <div className="dashboard-grid">
            <div className="chart-panel">
              <h3>Top Disease Distribution in Dataset</h3>
              {(stats?.top_diseases || []).map((item) => (
                <div className="bar-row" key={item.name}>
                  <span>{item.name}</span>
                  <div className="bar-track">
                    <i style={{ width: `${Math.min((item.count / (stats?.total_records || 100)) * 500, 100)}%` }} />
                  </div>
                  <b>{item.count} samples</b>
                </div>
              ))}
            </div>
            <div className="recent-panel">
              <h3>Recent Predictions & Vitals</h3>
              {(stats?.recent_predictions || []).length ? (
                stats.recent_predictions.map((item) => (
                  <div className="recent-item" key={item.id}>
                    <div className="recent-info">
                      <strong>{item.predicted_disease}</strong>
                      <span className="recent-sym">{item.vital_summary || item.symptoms}</span>
                    </div>
                    <b className="recent-conf">{item.confidence}%</b>
                  </div>
                ))
              ) : (
                <p className="empty-text">No predictions logged in this session yet.</p>
              )}
            </div>
          </div>
        </section>

        {/* ABOUT SECTION */}
        <section className="section about" id="about">
          <div className="section-heading">
            <span className="eyebrow"><Brain size={16} /> About Medi Mind</span>
            <h2>Educational Medical AI & Clinical Recommendation Engine</h2>
            <p>
              Built with Python FastAPI, MAX30102 Live Heart Rate Reader, Scikit-learn Logistic Regression, sublinear TF-IDF feature extraction,
              and interactive real-time dataset feedback loop.
            </p>
          </div>
          <div className="tech-grid">
            {['Python 3.13', 'FastAPI', 'MAX30102 / ESP32', 'Pandas', 'Scikit-learn', 'React 19', 'Vite 6', 'TF-IDF n-grams', 'Calibrated Probabilities'].map((tech) => (
              <span key={tech} className="tech-badge">{tech}</span>
            ))}
          </div>
        </section>

        {/* FAQ & CONTACT SECTION */}
        <section className="section faq-contact" id="contact">
          <div className="faq">
            <span className="eyebrow"><ChevronDown size={16} /> FAQ</span>
            <h2>Frequently Asked Questions</h2>
            {faqs.map((item) => (
              <details key={item.question}>
                <summary>{item.question}</summary>
                <p>{item.answer}</p>
              </details>
            ))}
          </div>
          <div className="contact-box">
            <h2>Contact & Clinical Collaboration</h2>
            <p>For research, model integration, or clinical trial feedback, connect with the Medi Mind team.</p>
            <a href="mailto:hello@medimind.local" className="contact-link">hello@medimind.local</a>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-brand">
          <HeartPulse size={20} />
          <span>Medi Mind AI Assistant</span>
        </div>
        <p>Educational healthcare technology platform. Always consult a licensed medical professional for real diagnoses.</p>
      </footer>
    </div>
  );
}

export default App;
