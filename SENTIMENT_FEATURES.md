# Sentiment-Based Alerts & Student Chat Support

This document describes the sentiment analysis and student support chat features implemented in the Student Risk Prediction System.

## 🌟 Features Overview

### 1. Sentiment Analysis Engine
- **Multi-method analysis**: Uses TextBlob and VADER sentiment analyzers
- **Emotional keyword detection**: Identifies distress signals and positive indicators
- **Academic stress detection**: Recognizes study-related pressure indicators
- **Risk level assessment**: Automatically categorizes as high, medium, or low risk
- **Confidence scoring**: Provides reliability metrics for analysis results

### 2. Student Support Chatbot
- **AI-powered responses**: Uses OpenAI GPT for contextual, empathetic conversations
- **Crisis detection**: Automatically identifies high-risk situations
- **Resource recommendations**: Provides relevant support resources based on context
- **Conversation memory**: Maintains context across chat sessions
- **Professional escalation**: Triggers counselor alerts for serious concerns

### 3. Feedback Submission System
- **Anonymous feedback**: Students can share concerns confidentially
- **Real-time sentiment analysis**: Immediate processing of emotional content
- **Automatic alerts**: Generates notifications for concerning feedback
- **Resource provision**: Offers relevant support resources based on sentiment

### 4. Sentiment Dashboard
- **Real-time monitoring**: Live view of student emotional wellbeing trends
- **Alert management**: Track and respond to high-risk situations
- **Trend analysis**: Visualize sentiment patterns over time
- **Intervention tracking**: Monitor counselor responses and outcomes

## 🚀 Getting Started

### Prerequisites
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   SECRET_KEY=your-secret-key-here
   ```

3. Initialize the database:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

### Running the Application
```bash
python app.py
```

## 📊 How It Works

### Sentiment Analysis Process
1. **Text Preprocessing**: Cleans and normalizes input text
2. **Multi-Algorithm Analysis**: 
   - TextBlob: Polarity (-1 to 1) and subjectivity (0 to 1)
   - VADER: Positive, negative, neutral, and compound scores
3. **Keyword Matching**: Searches for emotional indicators
4. **Risk Assessment**: Combines scores to determine overall risk level
5. **Resource Matching**: Suggests appropriate support resources

### Risk Level Classification
- **High Risk**: Contains crisis keywords, very negative sentiment, or self-harm indicators
- **Medium Risk**: Multiple stress indicators, moderately negative sentiment
- **Low Risk**: Neutral or positive sentiment, no concerning keywords

### Chatbot Response Types
- **General Support**: Empathetic listening and general guidance
- **Academic Stress**: Study strategies and academic resource recommendations
- **High Risk**: Crisis intervention protocols and immediate resource provision

## 🎯 Key Features

### For Students
- **Anonymous Feedback**: Share concerns without fear of judgment
- **24/7 Chat Support**: AI chatbot available anytime for emotional support
- **Immediate Resources**: Get relevant help resources based on your needs
- **Crisis Support**: Automatic connection to crisis hotlines when needed

### For Counselors/Staff
- **Real-time Alerts**: Immediate notifications for high-risk situations
- **Sentiment Trends**: Monitor student wellbeing patterns over time
- **Intervention Tracking**: Manage and track responses to student concerns
- **Conversation Summaries**: Review chat histories for better support

## 📈 Dashboard Features

### Statistics Overview
- Active high-risk alerts count
- Medium-risk alerts requiring attention
- Positive interaction trends
- Total student engagement metrics

### Alert Management
- View all active sentiment-based alerts
- Acknowledge and track alert responses
- Contact students directly from alerts
- Mark alerts as resolved

### Trend Analysis
- Sentiment score trends over time
- Risk level distribution charts
- Student interaction patterns
- Intervention effectiveness metrics

## 🔧 API Endpoints

### Student Endpoints
- `GET /student_support` - Student feedback and chat interface
- `POST /submit_feedback` - Submit feedback with sentiment analysis
- `POST /chat` - Send chat message to support bot

### Staff/Counselor Endpoints
- `GET /sentiment_dashboard` - Main sentiment monitoring dashboard
- `GET /api/sentiment_dashboard_data` - Dashboard data API
- `POST /api/acknowledge_alert/<id>` - Acknowledge sentiment alert

## 🛡️ Privacy & Security

### Data Protection
- All student interactions are stored securely in the database
- Sentiment analysis is performed locally (no external API for sentiment)
- Chat conversations maintain student anonymity options
- Counselor access is logged and tracked

### Crisis Protocols
- High-risk situations trigger immediate alerts
- Crisis resources are prominently displayed
- Emergency contacts are provided automatically
- Professional intervention is recommended when appropriate

## 🎨 User Interface

### Student Interface
- Clean, welcoming design with calming colors
- Easy-to-use feedback form with topic categories
- Interactive chat interface with typing indicators
- Prominent display of crisis resources when needed

### Staff Dashboard
- Professional monitoring interface
- Color-coded risk level indicators
- Interactive charts and trend visualizations
- Quick action buttons for student contact

## 📱 Mobile Responsiveness

All interfaces are fully responsive and work seamlessly on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🔮 Future Enhancements

### Planned Features
- **Predictive Analytics**: Identify at-risk students before crisis points
- **Integration with Campus Systems**: Connect with existing student information systems
- **Multi-language Support**: Provide support in multiple languages
- **Advanced Reporting**: Generate comprehensive wellbeing reports
- **Machine Learning Improvements**: Continuously improve sentiment accuracy

### Potential Integrations
- Campus counseling center scheduling systems
- Student information management systems
- Emergency notification systems
- Academic performance tracking systems

## 🆘 Crisis Resources

The system automatically provides these resources when high-risk situations are detected:

### Immediate Crisis Support
- **988 Suicide & Crisis Lifeline**: 24/7 crisis support
- **Crisis Text Line**: Text HOME to 741741
- **Campus Counseling Center**: Direct connection to local support

### Academic Support
- Tutoring centers
- Writing support services
- Study skills workshops
- Academic success coaching

## 📞 Support & Maintenance

### System Monitoring
- Regular database backups
- Sentiment analysis accuracy monitoring
- Chatbot response quality reviews
- Alert response time tracking

### Updates & Improvements
- Regular model updates for better accuracy
- New crisis keywords and indicators
- Enhanced resource recommendations
- User interface improvements based on feedback

## 🤝 Contributing

To contribute to the sentiment analysis features:

1. Review the existing sentiment analysis algorithms
2. Test with various input scenarios
3. Suggest improvements for accuracy
4. Provide feedback on user experience
5. Report any issues or bugs

## 📋 Testing Scenarios

### Test Cases for Sentiment Analysis
1. **Positive Feedback**: "I'm really enjoying my classes and feeling confident about my studies"
2. **Academic Stress**: "I'm overwhelmed with assignments and worried about failing my exams"
3. **High Risk**: "I can't take this anymore, everything feels hopeless"
4. **Mixed Sentiment**: "Some days are good but I'm struggling with anxiety"

### Expected Outcomes
- Positive feedback should show low risk with encouraging resources
- Academic stress should trigger medium risk with study support resources
- High-risk content should immediately alert counselors and provide crisis resources
- Mixed sentiment should provide balanced support and monitoring

This comprehensive sentiment analysis system provides a safety net for students while giving staff the tools they need to provide timely, appropriate support.
