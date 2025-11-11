# 🚀 Quick Start Guide

Get the Student Risk Prediction System running in 3 minutes!

## Step 1: Install Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Pandas & NumPy (data processing)
- Scikit-learn (machine learning)
- LangChain (AI agent framework)
- OpenAI (optional, for AI recommendations)

## Step 2: Run the Application

### Option A: Using the run script (Recommended)
```bash
python run.py
```

### Option B: Direct Flask run
```bash
python app.py
```

## Step 3: Access the Dashboard

Open your browser and go to:
```
http://localhost:5000
```

## 🎯 What You'll See

1. **Dashboard** - Overview of all students with risk statistics
2. **Students List** - Detailed list with filters
3. **Student Details** - Individual profiles with interventions
4. **Predict Risk** - Test the ML model with custom data
5. **Upload Data** - Add your own student CSV files

## 🔧 Optional: Enable AI Recommendations

For AI-powered intervention suggestions:

1. Get an OpenAI API key from https://platform.openai.com/
2. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` and add your key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Restart the application

**Note**: The system works perfectly without OpenAI using intelligent rule-based recommendations!

## 📊 Test the System

1. **View Dashboard**: See 30 sample students with risk levels
2. **Filter High Risk**: Click "High Risk Students" to see who needs help
3. **View Details**: Click any student to see personalized interventions
4. **Predict New**: Go to "Predict Risk" and enter test data:
   - Attendance: 45%
   - Average Score: 42%
   - Assignments: 5/10
   - Engagement: 35%
   - Click "Predict" to see the result

## 🎨 Features to Explore

- **Risk Distribution Chart**: Visual breakdown on dashboard
- **Progress Bars**: Color-coded metrics for each student
- **Intervention Priorities**: High/Medium/Low priority actions
- **CSV Upload**: Upload your own student data
- **API Endpoints**: `/api/students`, `/api/predict` for integrations

## 🛠 Troubleshooting

**Port already in use?**
```python
# Edit app.py, change the last line to:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Missing packages?**
```bash
pip install flask pandas numpy scikit-learn joblib langchain langchain-openai openai python-dotenv
```

**Model not training?**
- Ensure `data/sample_students.csv` exists
- Delete `models/saved_model.pkl` to force retrain

## 📝 Next Steps

1. **Customize Risk Logic**: Edit `models/risk_predictor.py`
2. **Add Interventions**: Modify `agents/intervention_agent.py`
3. **Change UI**: Update templates in `templates/` folder
4. **Add Your Data**: Upload CSV via the web interface

## 🎓 Understanding the System

**How Risk is Calculated**:
- Attendance < 50% → +3 risk points
- Score < 50% → +3 risk points
- Engagement < 40% → +2 risk points
- Assignments < 50% → +2 risk points
- **Total ≥6**: High Risk
- **Total 3-5**: Medium Risk
- **Total <3**: Safe

**ML Model**:
- Algorithm: Random Forest Classifier
- Features: Attendance, Score, Assignments, Engagement
- Output: Risk level + confidence score

**AI Interventions**:
- Uses LangChain to generate personalized advice
- Falls back to rule-based if no API key
- Provides priority levels and timelines

---

**Need Help?** Check `README.md` for detailed documentation!

**Ready to Deploy?** The system is production-ready with proper error handling and scalability!
