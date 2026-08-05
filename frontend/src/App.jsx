import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  CheckCircle2,
  ChevronDown,
  HeartPulse,
  Loader2,
  Menu,
  Microscope,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Upload,
  X,
} from 'lucide-react';
import { getStats, predictDisease } from './services/api';

const initialQuestionnaire = {
  patientName: '',
  age: '',
  sex: '',
  symptomGroup: '',
  symptomDuration: '',
  severity: '',
  symptoms: '',
  preExistingConditions: [],
};

const navItems = [
  { id: 'home', label: 'Home' },
  { id: 'detect', label: 'Detect' },
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'about', label: 'About' },
  { id: 'contact', label: 'Contact' },
];

const faqs = [
  {
    question: 'Does Medi Mind diagnose medical conditions?',
    answer: 'No. It provides educational predictions from symptom text and should be reviewed with a qualified clinician.',
  },
  {
    question: 'Can it analyze medical images?',
    answer: 'The current model is trained on symptom descriptions, so image upload is only a preview aid unless an image model is added.',
  },
  {
    question: 'What model does this use?',
    answer: 'It uses TF-IDF text features with a Multinomial Naive Bayes classifier trained on the included symptom dataset.',
  },
];

const features = [
  { icon: Brain, title: 'Symptom Intelligence', text: 'Predicts likely disease categories from natural-language patient concerns.' },
  { icon: ShieldCheck, title: 'Safety First', text: 'Includes emergency level hints, disclaimers, and clinician guidance.' },
  { icon: BarChart3, title: 'Live Insights', text: 'Summarizes dataset coverage, disease frequency, and recent predictions.' },
];

const symptomGroups = [
  'Headache and migraine',
  'Fever and body ache',
  'Cough, cold, or throat pain',
  'Stomach pain, acidity, or vomiting',
  'Urinary burning or lower abdominal pain',
  'Breathing difficulty or wheezing',
  'Chest pain or blood pressure concern',
  'Joint pain or swelling',
  'Skin allergy or infection',
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
  const [questionnaire, setQuestionnaire] = useState(initialQuestionnaire);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((error) => setStatsError(error.message));
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
      const result = await predictDisease({
        symptoms: questionnaire.symptoms,
        patient_name: questionnaire.patientName,
        age: Number(questionnaire.age),
        sex: questionnaire.sex || null,
        symptom_group: questionnaire.symptomGroup,
        symptom_duration: questionnaire.symptomDuration || null,
        severity: questionnaire.severity || null,
        pre_existing_conditions: questionnaire.preExistingConditions,
        image_filename: null,
      });
      setPrediction(result);
      const nextStats = await getStats();
      setStats(nextStats);
    } catch (error) {
      setNotice(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="site-header">
        <button className="brand" onClick={() => scrollTo('home')} aria-label="Go to home">
          <span className="brand-mark"><HeartPulse size={22} /></span>
          <span>Medi Mind</span>
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
        <section className="hero section" id="home">
          <div className="hero-copy">
            <span className="eyebrow"><Sparkles size={16} /> AI symptom assistant</span>
            <h1>Medi Mind helps turn symptom descriptions into clear next steps.</h1>
            <p>
              A professional web experience for the existing disease prediction model, combining AI output,
              emergency hints, care suggestions, and a transparent medical disclaimer.
            </p>
            <div className="hero-actions">
              <button className="primary-button" onClick={() => scrollTo('detect')}>
                Start detection <ArrowRight size={18} />
              </button>
              <button className="secondary-button" onClick={() => scrollTo('about')}>View model details</button>
            </div>
          </div>
          <div className="hero-visual" aria-label="Medical analytics illustration">
            <div className="pulse-card">
              <Activity size={30} />
              <span>Model accuracy</span>
              <strong>{stats ? `${stats.accuracy}%` : 'Loading'}</strong>
            </div>
            <div className="signal-panel">
              <span />
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="diagnosis-chip"><Stethoscope size={18} /> Symptom-based prediction</div>
          </div>
        </section>

        <section className="section overview">
          <div className="section-heading">
            <span className="eyebrow"><Microscope size={16} /> Disease detection</span>
            <h2>Built around the model that already exists.</h2>
            <p>
              Medi Mind keeps the trained-at-runtime TF-IDF and Naive Bayes pipeline intact while adding the
              product layer a real user expects.
            </p>
          </div>
          <div className="feature-grid">
            {features.map(({ icon: Icon, title, text }) => (
              <article className="feature-card" key={title}>
                <Icon />
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section split how-it-works">
          <div>
            <span className="eyebrow"><CheckCircle2 size={16} /> How it works</span>
            <h2>From symptoms to structured guidance.</h2>
          </div>
          <div className="steps">
            {['Describe symptoms in plain language', 'API cleans text and runs the ML pipeline', 'Results return with confidence and safety context'].map((step, index) => (
              <div className="step" key={step}>
                <span>{index + 1}</span>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="section detector" id="detect">
          <div className="section-heading">
            <span className="eyebrow"><Upload size={16} /> Detection</span>
            <h2>Patient questionnaire.</h2>
            <p>Fill in the patient details, select the closest symptom group, and describe symptoms clearly for prediction.</p>
          </div>
          <div className="detector-layout">
            <form className="detector-form" onSubmit={handlePredict}>
              <div className="form-grid">
                <div className="field">
                  <label htmlFor="patientName">Patient name</label>
                  <input
                    id="patientName"
                    value={questionnaire.patientName}
                    onChange={(event) => updateQuestion('patientName', event.target.value)}
                    placeholder="Enter full name"
                  />
                </div>
                <div className="field">
                  <label htmlFor="age">Age</label>
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
                <div className="field">
                  <label htmlFor="sex">Sex</label>
                  <select id="sex" value={questionnaire.sex} onChange={(event) => updateQuestion('sex', event.target.value)}>
                    <option value="">Select</option>
                    <option>Female</option>
                    <option>Male</option>
                    <option>Other</option>
                    <option>Prefer not to say</option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="severity">Severity</label>
                  <select id="severity" value={questionnaire.severity} onChange={(event) => updateQuestion('severity', event.target.value)}>
                    <option value="">Select</option>
                    <option>Mild</option>
                    <option>Moderate</option>
                    <option>Severe</option>
                  </select>
                </div>
              </div>

              <div className="field">
                <label htmlFor="symptomGroup">Closest symptom category</label>
                <select
                  id="symptomGroup"
                  value={questionnaire.symptomGroup}
                  onChange={(event) => updateQuestion('symptomGroup', event.target.value)}
                >
                  <option value="">Choose a category</option>
                  {symptomGroups.map((group) => <option key={group}>{group}</option>)}
                </select>
              </div>

              <div className="field">
                <label htmlFor="duration">How long has this been happening?</label>
                <select
                  id="duration"
                  value={questionnaire.symptomDuration}
                  onChange={(event) => updateQuestion('symptomDuration', event.target.value)}
                >
                  <option value="">Select duration</option>
                  <option>Today</option>
                  <option>1-2 days</option>
                  <option>3-7 days</option>
                  <option>More than a week</option>
                  <option>Long-term or recurring</option>
                </select>
              </div>

              <div className="field">
                <label>Pre-existing disease or condition</label>
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

              <label htmlFor="symptoms">Describe current symptoms</label>
              <textarea
                id="symptoms"
                value={questionnaire.symptoms}
                onChange={(event) => updateQuestion('symptoms', event.target.value)}
                placeholder="Example: severe headache with nausea and sensitivity to light since yesterday"
              />

              {/* Image upload is intentionally paused until an image model is added. */}

              {notice && <p className="notice">{notice}</p>}

              <button className="primary-button full" disabled={loading} type="submit">
                {loading ? <Loader2 className="spin" size={18} /> : <Brain size={18} />}
                {loading ? 'Analyzing symptoms' : 'Analyze'}
              </button>
            </form>

            <aside className="result-panel">
              {prediction ? (
                <>
                  <div className="result-header">
                    <span>Prediction for {questionnaire.patientName}</span>
                    <strong>{prediction.predicted_disease}</strong>
                  </div>
                  <div className="patient-summary">
                    <span>{questionnaire.age} years</span>
                    {questionnaire.sex && <span>{questionnaire.sex}</span>}
                    {questionnaire.symptomGroup && <span>{questionnaire.symptomGroup}</span>}
                  </div>
                  <div className="confidence" style={confidenceStyle}>
                    <span><b>{prediction.confidence}%</b> confidence</span>
                    <div><i /></div>
                  </div>
                  <div className={`emergency emergency-${prediction.emergency_level.toLowerCase()}`}>
                    {prediction.emergency_level} emergency signal
                  </div>
                  <p>{prediction.explanation}</p>
                  <dl className="result-list">
                    <div>
                      <dt>Doctor</dt>
                      <dd>{prediction.doctor_recommendation}</dd>
                    </div>
                    <div>
                      <dt>Remedies</dt>
                      <dd>{prediction.remedies.length ? prediction.remedies.join(', ') : 'Consult a clinician for personalized care.'}</dd>
                    </div>
                    <div>
                      <dt>Disclaimer</dt>
                      <dd>{prediction.disclaimer}</dd>
                    </div>
                  </dl>
                </>
              ) : (
                <div className="empty-state">
                  <Stethoscope size={42} />
                  <h3>Your results will appear here.</h3>
                  <p>Enter symptoms and run analysis to see prediction, confidence, and guidance.</p>
                </div>
              )}
            </aside>
          </div>
        </section>

        <section className="section dashboard" id="dashboard">
          <div className="section-heading">
            <span className="eyebrow"><BarChart3 size={16} /> Dashboard</span>
            <h2>Dataset and prediction overview.</h2>
          </div>
          {statsError && <p className="notice">{statsError}</p>}
          <div className="stats-grid">
            <div className="stat"><span>Records</span><strong>{stats?.total_records ?? '--'}</strong></div>
            <div className="stat"><span>Diseases</span><strong>{stats?.total_diseases ?? '--'}</strong></div>
            <div className="stat"><span>Accuracy</span><strong>{stats ? `${stats.accuracy}%` : '--'}</strong></div>
          </div>
          <div className="dashboard-grid">
            <div className="chart-panel">
              <h3>Top diseases</h3>
              {(stats?.top_diseases || []).map((item) => (
                <div className="bar-row" key={item.name}>
                  <span>{item.name}</span>
                  <div><i style={{ width: `${Math.min(item.count, 90)}%` }} /></div>
                  <b>{item.count}</b>
                </div>
              ))}
            </div>
            <div className="recent-panel">
              <h3>Recent predictions</h3>
              {(stats?.recent_predictions || []).length ? (
                stats.recent_predictions.map((item) => (
                  <div className="recent-item" key={item.id}>
                    <span>{item.predicted_disease}</span>
                    <b>{item.confidence}%</b>
                  </div>
                ))
              ) : (
                <p>No predictions in this session yet.</p>
              )}
            </div>
          </div>
        </section>

        <section className="section about" id="about">
          <div className="section-heading">
            <span className="eyebrow"><Brain size={16} /> About</span>
            <h2>Transparent AI for educational healthcare prototypes.</h2>
            <p>
              The backend trains a scikit-learn pipeline from the included CSV at startup. It does not retrain
              externally, change labels, or use an image model.
            </p>
          </div>
          <div className="tech-grid">
            {['Python', 'FastAPI', 'Pandas', 'Scikit-learn', 'React', 'Vite'].map((tech) => <span key={tech}>{tech}</span>)}
          </div>
          <div className="team">
            <h3>Team</h3>
            <div className="team-grid">
              {['Project Lead', 'ML Engineer', 'Frontend Designer'].map((role) => (
                <article className="team-card" key={role}>
                  <span>{role.charAt(0)}</span>
                  <h4>{role}</h4>
                  <p>Placeholder profile</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section faq-contact" id="contact">
          <div className="faq">
            <span className="eyebrow"><ChevronDown size={16} /> FAQ</span>
            {faqs.map((item) => (
              <details key={item.question}>
                <summary>{item.question}</summary>
                <p>{item.answer}</p>
              </details>
            ))}
          </div>
          <div className="contact-box">
            <h2>Contact</h2>
            <p>For academic demos, integrations, or model upgrades, connect with the Medi Mind team.</p>
            <a href="mailto:hello@medimind.local">hello@medimind.local</a>
          </div>
        </section>
      </main>

      <footer>
        <span>Medi Mind</span>
        <p>Educational AI assistant. Always consult a licensed medical professional.</p>
      </footer>
    </div>
  );
}

export default App;
