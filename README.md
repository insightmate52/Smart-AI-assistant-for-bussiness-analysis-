# InsightMate – AI-Powered Data Insights Platform

InsightMate is an AI-powered data analysis platform that helps users extract meaningful insights from datasets automatically. The system combines data analysis techniques with AI-powered interpretation to generate intelligent insights, forecasts, and explanations from uploaded datasets.

The application allows users to upload data, analyze patterns, detect potential issues, and generate visual insights through an interactive web interface.

---

## Key Features

• Upload datasets for automated analysis  
• AI-powered insight generation from data  
• Forecasting and pattern detection  
• Red flag detection for unusual trends or anomalies  
• Data visualization and structured insights  
• Interactive chat interface for exploring insights  
• Clean and user-friendly web interface  

---

## Technologies Used

### Programming Language
Python

### Backend Framework
Flask

### AI Integration
Google Gemini API

### Data Processing
Pandas  
NumPy  

### Visualization
Matplotlib  
Seaborn  

### Frontend
HTML  
CSS  
Jinja Templates  

---

## Project Architecture

The project follows a modular structure separating AI processing, backend routes, templates, and utilities.
INSIGHTMATE
│
├── chat
│ ├── init.py
│ ├── gemini_client.py
│ ├── llm.py
│ ├── prompts.py
│ └── routes.py
│
├── ml
│ ├── init.py
│ ├── forecast_engine.py
│ ├── insight_core.py
│ ├── insight_engine.py
│ ├── red_flag_engine.py
│ └── utils.py
│
├── models
│
├── static
│ ├── insights
│ └── styles.css
│
├── templates
│ ├── base.html
│ ├── chat.html
│ ├── estimate.html
│ ├── insights.html
│ ├── login.html
│ └── upload.html
│
├── app.py
├── auth.py
├── requirements.txt
├── test_api.py
├── test_upload_endpoints.py
├── .env
└── README.md

---
## System Workflow

1. The user uploads a dataset through the web interface.
2. The system processes the dataset using Python data analysis libraries.
3. The **Insight Engine** identifies patterns, correlations, and important statistics.
4. The **Forecast Engine** predicts trends in the dataset.
5. The **Red Flag Engine** detects anomalies or unusual behavior.
6. The AI module (Gemini API) generates natural language explanations of the insights.
7. Results are presented through charts, insights pages, and the chat interface.

---

## Core Components

### Insight Engine
Generates statistical insights and key patterns from the dataset.

### Forecast Engine
Predicts potential trends and future behavior in the data.

### Red Flag Engine
Detects anomalies, unusual patterns, and possible risks within the dataset.

### AI Chat Module
Uses Gemini API to provide explanations and answer questions related to the data insights.

---

## Use Cases

• Quick exploratory data analysis  
• AI-assisted dataset understanding  
• Business trend analysis  
• Educational demonstrations of data insights  
• Data anomaly detection  

---

## Future Improvements

• Interactive dashboards  
• More advanced machine learning models  
• Support for additional file formats (Excel, JSON)  
• Exportable reports and automated summaries  
• Improved AI-driven recommendations  

---

## Author

Priyanka Gadekar,Dishti Andersahare, Shruti Mishra
BTech Data Science Students

Interested in Artificial Intelligence, Data Science, and Data Visualization.
Interested in Artificial Intelligence, Data Science, and Data Visualization.
