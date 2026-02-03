# AI Resume Analyzer

An intelligent resume analysis platform powered by Google's Gemini AI that provides real-time feedback, skill assessments, and personalized course recommendations.

## Features

- 🔐 **User Authentication**: Secure signup and login system with MongoDB
- 🤖 **AI-Powered Resume Analysis**: Upload your resume and get instant feedback using Gemini AI
- 📊 **Comprehensive Feedback**: Receive detailed analysis including:
  - Overall assessment
  - Strengths identification
  - Areas for improvement
  - Missing skills detection
  - Career suggestions
- 📚 **Course Recommendations**: Get personalized course suggestions based on your resume analysis
- 🎯 **Skill Assessments**: Test your knowledge with MCQ-based assessments:
  - SQL Assessment (10 questions)
  - Data Structures Assessment (10 questions)
- 📈 **Score Tracking**: View your latest assessment scores on the dashboard
- 💾 **Data Persistence**: All scores are saved to MongoDB and associated with your account

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- MongoDB (local installation or MongoDB Atlas connection string)

### Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gemini API Key**:
   
   On macOS/Linux:
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```
   
   On Windows:
   ```cmd
   set GEMINI_API_KEY=your-api-key-here
   ```

4. **Set up MongoDB**:
   
   **Option A: Local MongoDB**
   - Install MongoDB locally: https://www.mongodb.com/try/download/community
   - The app will connect to `mongodb://localhost:27017/` by default
   
   **Option B: MongoDB Atlas (Cloud)**
   - Create a free cluster at https://www.mongodb.com/cloud/atlas
   - Get your connection string and set it:
   ```bash
   export MONGO_URI='mongodb+srv://username:password@cluster.mongodb.net/'
   ```
   
   The app will use `mongodb://localhost:27017/` by default if `MONGO_URI` is not set.

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Resume Analysis

1. Click on the "Resume Analysis" tab
2. Upload your resume (PDF or TXT format)
3. Wait for AI analysis (usually takes 10-30 seconds)
4. Review the comprehensive feedback including:
   - Overall assessment
   - Your strengths
   - Areas for improvement
   - Missing skills
   - Recommended courses
   - Career suggestions

### Skill Assessments

1. Click on the "Skill Assessments" tab
2. Choose an assessment (SQL or Data Structures)
3. Answer all MCQ questions
4. Click "Submit Assessment" to see your results
5. Review your score and detailed answer explanations

## Project Structure

```
AI Platform/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend UI
├── uploads/              # Uploaded resume files (created automatically)
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/upload-resume` - Upload and analyze resume
- `GET /api/assessments` - Get list of available assessments
- `GET /api/assessments/<id>` - Get assessment questions
- `POST /api/assessments/<id>/submit` - Submit assessment answers

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Google Gemini API
- **Frontend**: HTML, CSS, JavaScript
- **File Processing**: PyPDF2 for PDF extraction

## Notes

- Maximum file size: 16MB
- Supported resume formats: PDF, TXT
- The application stores uploaded files in the `uploads/` directory
- Make sure to keep your Gemini API key secure and never commit it to version control

## Future Enhancements

- Add more skill assessments (Python, JavaScript, etc.)
- Support for DOCX file format
- User accounts and progress tracking
- Export analysis reports as PDF
- Integration with online course platforms

## License

This project is open source and available for personal and educational use.
