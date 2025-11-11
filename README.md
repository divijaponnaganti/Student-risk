# 🎓 Student Risk Prediction System

An AI-powered system that predicts which students are at risk of academic failure and provides personalized intervention recommendations to help educators take proactive action.

## 🌟 Features

### **Core Features:**
- **ML-Based Risk Prediction**: Uses Random Forest algorithm to analyze student data and predict risk levels
- **AI-Powered Interventions**: Generates personalized recommendations using LangChain (with optional OpenAI integration)
- **Interactive Dashboard**: Beautiful web interface for monitoring all students
- **Real-Time Analysis**: Instant risk assessment for new students
- **Data Upload**: Easy CSV upload for batch processing

### **🚀 Enhanced Features:**
- **📄 PDF Report Generation**: Professional reports with AI suggestions and complete analysis
- **📧 Automated Notifications**: Email/SMS alerts to parents for high-risk students
- **🤖 LLM-Powered Suggestions**: Detailed, personalized feedback using GPT integration
- **📊 Bulk Operations**: Generate reports and send alerts for multiple students
- **📱 Notification Tracking**: Complete history of all sent alerts and communications
- **👥 Contact Management**: Integrated parent, student, and teacher contact information

## 🔄 How It Works

1. **Data Collection**: System analyzes attendance, scores, engagement, and assignment completion
2. **Risk Prediction**: ML model classifies students into High Risk, Medium Risk, or Safe
3. **AI Recommendations**: Generates personalized intervention strategies
4. **Educator Action**: Dashboard provides clear action items for each at-risk student

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd c:/Users/DIVIJA/CascadeProjects/windsurf-project
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **(Optional) Configure OpenAI API**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key for AI-powered recommendations
   - If not configured, system will use rule-based recommendations

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

1. **Start the Flask server**:
```bash
python app.py
```

2. **Access the dashboard**:
   - Open your browser and go to: `http://localhost:5000`

3. **The system will automatically**:
   - Load sample student data
   - Train the ML model (first run only)
   - Display the dashboard

## 📊 Data Format

Your CSV file should include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| StudentID | Unique identifier | S001 |
| Name | Student name | Alice Johnson |
| Attendance | Attendance % (0-100) | 92 |
| AverageScore | Average score % (0-100) | 85 |
| AssignmentsSubmitted | Number submitted | 10 |
| TotalAssignments | Total assignments | 10 |
| EngagementScore | Engagement % (0-100) | 88 |
| PreviousGrade | Previous grade | A |

**Sample CSV**:
```csv
StudentID,Name,Attendance,AverageScore,AssignmentsSubmitted,TotalAssignments,EngagementScore,PreviousGrade
S001,Alice Johnson,92,85,10,10,88,A
S002,Bob Smith,45,42,5,10,35,C
```

## 🎯 Risk Classification

The system classifies students into three categories:

- 🔴 **High Risk**: Requires immediate intervention (attendance < 50% OR score < 50%)
- 🟡 **Medium Risk**: Needs monitoring (attendance 50-75% OR score 50-70%)
- 🟢 **Safe**: On track (good attendance and scores)

## 💡 Key Features Explained

### 1. Dashboard
- Overview statistics
- Risk distribution chart
- Quick access to at-risk students

### 2. Student List
- Filter by risk level
- Visual progress bars
- Quick access to details

### 3. Student Details
- Complete profile
- Risk assessment
- Personalized interventions
- Priority-based action items

### 4. Risk Prediction
- Predict risk for new students
- Real-time ML inference
- Confidence scores

### 5. Data Upload
- Batch process student data
- Automatic risk calculation
- CSV format validation

## 🛠 Tech Stack

- **Backend**: Flask (Python web framework)
- **ML Model**: Scikit-learn (Random Forest Classifier)
- **AI Agent**: LangChain + OpenAI (optional)
- **Frontend**: Bootstrap 5, Chart.js
- **Data Processing**: Pandas, NumPy

## 📁 Project Structure

```
windsurf-project/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env.example               # Environment variables template
├── data/
│   └── sample_students.csv    # Sample student data
├── models/
│   ├── risk_predictor.py      # ML prediction model
│   └── saved_model.pkl        # Trained model (auto-generated)
├── agents/
│   └── intervention_agent.py  # AI intervention generator
└── templates/                 # HTML templates
    ├── base.html
    ├── dashboard.html
    ├── students.html
    ├── student_detail.html
    ├── predict.html
    ├── predict_result.html
    └── upload.html
```

## 🔧 Configuration

### With OpenAI (AI-Powered Recommendations)
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add to `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

### Without OpenAI (Rule-Based Recommendations)
- System works perfectly without OpenAI
- Uses intelligent rule-based intervention system
- No API key needed

## 📈 Model Training

The ML model is automatically trained on first run using the sample data. To retrain:

```python
from models.risk_predictor import StudentRiskPredictor

predictor = StudentRiskPredictor()
predictor.train_model('data/sample_students.csv')
predictor.save_model('models/saved_model.pkl')
```

## 🎨 Screenshots

### Dashboard
- Real-time statistics
- Risk distribution visualization
- Quick action buttons

### Student Details
- Comprehensive profile
- Visual metrics
- Prioritized interventions

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Add more features
- Improve the ML model
- Enhance the UI
- Add more intervention strategies

## 📝 License

This project is for educational purposes.

## 🆘 Troubleshooting

**Issue**: Model not training
- **Solution**: Ensure `data/sample_students.csv` exists

**Issue**: OpenAI errors
- **Solution**: Check API key in `.env` or disable by not setting the key

**Issue**: Port 5000 already in use
- **Solution**: Change port in `app.py`: `app.run(port=5001)`

## 📧 Support

For issues or questions, check the code comments or modify as needed for your use case.

---

**Built with ❤️ using Flask, Scikit-learn, and LangChain**
