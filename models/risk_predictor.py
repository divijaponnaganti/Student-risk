"""
Student Risk Prediction Model
Uses ML to predict which students are at risk of academic failure
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os


class StudentRiskPredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = ['Attendance', 'AverageScore', 'AssignmentsSubmitted', 
                                'TotalAssignments', 'EngagementScore']
        
    def prepare_data(self, df):
        """Prepare and clean the data"""
        # Calculate assignment completion rate
        df['AssignmentCompletionRate'] = (df['AssignmentsSubmitted'] / df['TotalAssignments']) * 100
        
        # Encode previous grades
        grade_mapping = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
        df['PreviousGradeNumeric'] = df['PreviousGrade'].map(grade_mapping)
        
        # Define risk level based on multiple factors
        df['RiskLevel'] = df.apply(self._calculate_risk, axis=1)
        
        return df
    
    def _calculate_risk(self, row):
        """Calculate risk level based on student metrics"""
        # New risk categorization based on attendance requirements
        attendance = row['Attendance']
        
        # Primary classification based on attendance
        if attendance >= 75:
            return 'Safe'
        elif attendance >= 70:
            return 'Medium Risk'
        elif attendance >= 60:
            return 'High Risk'
        else:
            return 'Critical Risk'
    
    def train_model(self, data_path):
        """Train the risk prediction model"""
        # Load data
        df = pd.read_csv(data_path)
        df = self.prepare_data(df)
        
        # Prepare features
        X = df[self.feature_columns]
        y = df['RiskLevel']
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        # Calculate accuracy
        accuracy = self.model.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.2%}")
        
        return accuracy
    
    def predict_risk(self, student_data):
        """Predict risk level for a student"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Prepare features
        features = [[
            student_data['Attendance'],
            student_data['AverageScore'],
            student_data['AssignmentsSubmitted'],
            student_data['TotalAssignments'],
            student_data['EngagementScore']
        ]]
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        risk_level = self.label_encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities) * 100
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'probabilities': {
                label: prob * 100 
                for label, prob in zip(self.label_encoder.classes_, probabilities)
            }
        }
    
    def save_model(self, path='models/saved_model.pkl'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns
        }, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path='models/saved_model.pkl'):
        """Load a trained model"""
        data = joblib.load(path)
        self.model = data['model']
        self.label_encoder = data['label_encoder']
        self.feature_columns = data['feature_columns']
        print(f"Model loaded from {path}")


if __name__ == "__main__":
    # Train and save the model
    predictor = StudentRiskPredictor()
    predictor.train_model('data/sample_students.csv')
    predictor.save_model()
