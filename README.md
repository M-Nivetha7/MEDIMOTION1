## Complete README.md - Copy and Paste

```markdown
# 🏥 MediMotion - AI Physiotherapy Tracker

<div align="center">

![React](https://img.shields.io/badge/React-18.2.0-blue.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**Real-time AI-powered physiotherapy exercise tracking with skeleton visualization**

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Tech Stack](#-technology-stack) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📋 Overview

MediMotion is an AI-powered physiotherapy exercise tracker that provides real-time pose detection, joint angle measurement, and intelligent form feedback. It helps patients perform their rehabilitation exercises correctly by visualizing their movements with a skeleton overlay and providing instant feedback.

### 🎯 Key Benefits

- ✅ **Real-time feedback** - Instant correction during exercises
- ✅ **Visual guidance** - Green skeleton overlay shows proper form
- ✅ **Progress tracking** - Session history and performance scores
- ✅ **Professional reports** - PDF reports for physiotherapists
- ✅ **No equipment needed** - Just a camera and your device

---

## ✨ Features

### Core Features
- **Real-time Skeleton Tracking** - Green lines connecting all your joints
- **Live Joint Angle Measurement** - Accurate angles for shoulders, elbows, and knees
- **AI-Powered Feedback** - Instant form correction and performance scoring
- **Multiple Exercises** - Shoulder Raise, Elbow Curl, Knee Bend

### Advanced Features
- **Session History** - Track your progress over time
- **PDF Reports** - Generate detailed exercise reports
- **User Authentication** - Secure login and data storage
- **Performance Analytics** - Visual charts and progress tracking

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Check Command |
|-------------|---------|----------------|
| Node.js | 16+ | `node --version` |
| npm | 8+ | `npm --version` |
| Python (backend only) | 3.11+ | `python3 --version` |

### Installation & Running

#### Option 1: Frontend Only (Recommended - Simpler)

This option runs the complete exercise tracking without any backend setup.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/physiotherapy-app.git
cd physiotherapy-app/frontend

# Install dependencies (first time only)
npm install

# Start the application
npm start
```

**Your browser will automatically open to http://localhost:3000**

#### Option 2: Full Stack (Frontend + Backend)

Use this option for session history, PDF reports, and user authentication.

**Terminal 1 - Backend Server:**
```bash
cd physiotherapy-app/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

**Terminal 2 - Frontend App:**
```bash
cd physiotherapy-app/frontend

# Install dependencies (first time only)
npm install

# Start the app
npm start
```

### Quick Setup Scripts

For easier setup, use the provided scripts:

```bash
# Make scripts executable (Mac/Linux)
chmod +x setup.sh start.sh

# First time setup
./setup.sh

# Start the application
./start.sh
```

---

## 📱 Usage Guide

### Step-by-Step Instructions

1. **Allow Camera Access**
   - Click "Allow" when your browser requests camera permission
   - Make sure no other app is using your camera

2. **Select Your Exercise**
   - 🏋️ **Shoulder Raise** - Lift arms up and down (Target: 150-180°)
   - 💪 **Elbow Curl** - Bend and straighten elbows (Target: 160-180°)
   - 🦵 **Knee Bend** - Squat motion (Target: 150-170°)

3. **Start Tracking**
   - Click the **"START TRACKING"** button
   - The green skeleton overlay will appear

4. **Position Yourself**
   - Stand **6-8 feet away** from the camera
   - Ensure your **entire body** (head to feet) is visible
   - Face the camera directly

5. **Perform the Exercise**
   - Follow the green skeleton lines
   - Watch the real-time angle measurements
   - Read the AI feedback for improvements

### What You'll See on Screen

| Visual Element | Meaning |
|---------------|---------|
| 🟢 **Green Lines** | Skeleton connecting your joints |
| 🔴 **Red Dots** | Joint positions (shoulders, elbows, wrists, hips, knees, ankles) |
| 📐 **Numbers on Camera** | Real-time angle measurements on your body |
| 📊 **Right Panel** | Detailed angle values with progress bars |
| 🟡 **Score** | Performance percentage (0-100%) |
| 💬 **Feedback** | AI-powered form suggestions |

---

## 📊 Performance Scoring System

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100% | 🎉 Excellent | Perfect form! Full range of motion achieved |
| 70-89% | 💪 Good | Good effort! Try to extend a bit more |
| 50-69% | 📈 Fair | Keep practicing! Focus on range of motion |
| Below 50% | 📋 Needs Work | Slow down and focus on proper form |

### How Score is Calculated

- **Angle > 150°** → 90 points
- **Angle 120-150°** → 70 points
- **Angle < 120°** → 50 points
- **Final Score** = Average of all joint angles

---

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | User interface framework |
| **MediaPipe.js** | Pose detection and skeleton tracking |
| **TensorFlow.js** | Machine learning model execution |
| **HTML5 Canvas** | Real-time skeleton rendering |

### Backend (Optional)
| Technology | Purpose |
|------------|---------|
| **Flask** | REST API server |
| **MediaPipe** | Pose detection |
| **OpenCV** | Image processing |
| **ReportLab** | PDF report generation |
| **JWT** | Authentication tokens |

---

## 📁 Project Structure

```
physiotherapy-app/
│
├── frontend/                    # React application
│   ├── public/
│   │   └── index.html          # Main HTML file
│   ├── src/
│   │   └── App.js              # Main React component
│   ├── package.json            # Node dependencies
│   └── package-lock.json       # Locked dependencies
│
├── backend/                     # Flask backend (optional)
│   ├── app.py                  # Main Flask application
│   ├── pose_tracker.py         # Pose detection logic
│   ├── auth.py                 # User authentication
│   ├── feedback.py             # AI feedback generation
│   ├── report.py               # PDF report generation
│   ├── utils.py                # Utility functions
│   ├── requirements.txt        # Python dependencies
│   └── data/                   # User data storage
│       ├── sessions/           # Exercise session history
│       └── reports/            # Generated PDF reports
│
├── README.md                   # This file
├── setup.sh                    # Setup script
└── start.sh                    # Start script
```

---

## 💡 Tips for Best Results

### Camera Positioning
```
        Camera
           |
           |
    ← 6-8 feet →
           |
        You
```

### Lighting Tips
- ✅ Use bright, even lighting
- ✅ Position light source in front of you
- ❌ Avoid backlighting (light behind you)
- ❌ Avoid dark shadows on your body

### Clothing Tips
- ✅ Wear solid, contrasting colors
- ✅ Ensure arms and legs are visible
- ❌ Avoid all-black or all-white clothing
- ❌ Avoid very loose or baggy clothes

### Movement Tips
- ✅ Perform exercises slowly and controlled
- ✅ Focus on form rather than speed
- ✅ Watch the skeleton lines for guidance
- ✅ Breathe steadily throughout

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Camera Not Working
```bash
# Check if camera is being used by another app
# Close Zoom, Teams, or other video apps
# Refresh the page and allow camera access
# Check browser permissions
```

#### Skeleton Not Showing
| Issue | Solution |
|-------|----------|
| Standing too close | Move back to 6-8 feet |
| Poor lighting | Add more light in front of you |
| Dark clothing | Wear lighter contrasting colors |
| Partial body | Make sure full body is visible |

#### Port 3000 Already in Use
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9
npm start
```

#### npm Start Fails
```bash
# Clean reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

#### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Restart backend
cd backend
source venv/bin/activate
python app.py
```

#### Angles Not Accurate
- Stand further back (full body visible)
- Improve lighting
- Wear contrasting clothes
- Face camera directly
- Move slowly

---

## 📝 API Endpoints (Backend)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Health check | No |
| POST | `/api/analyze_pose` | Analyze pose from image | No |
| POST | `/api/save_session` | Save exercise session | Yes |
| GET | `/api/get_history/<username>` | Get user history | Yes |
| POST | `/api/login` | User login | No |
| POST | `/api/signup` | User registration | No |
| GET | `/api/generate_report` | Generate PDF report | Yes |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/physiotherapy-app.git

# Install dependencies
cd physiotherapy-app/frontend
npm install

# Start development server
npm start
```

---

## 📄 License

This project is licensed under the MIT License - see below:

```
MIT License

Copyright (c) 2024 MediMotion

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

Full license text: https://opensource.org/licenses/MIT
```

---

## 🙏 Acknowledgments

- **MediaPipe** - Google's amazing pose detection technology
- **TensorFlow.js** - Machine learning in the browser
- **React** - UI framework
- **Flask** - Python web framework
- **OpenCV** - Computer vision library

---

## 📞 Support & Contact

### Getting Help

- 📖 **Documentation**: Check this README first
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/YOUR_USERNAME/physiotherapy-app/issues)
- 💬 **Discussions**: Join the [GitHub Discussions](https://github.com/YOUR_USERNAME/physiotherapy-app/discussions)

### Feature Requests

Have an idea for a new feature? 
- Open a [Feature Request](https://github.com/YOUR_USERNAME/physiotherapy-app/issues/new)
- Describe the feature and its benefits
- We'll review and prioritize accordingly

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Real-time pose detection
- ✅ Skeleton visualization
- ✅ Angle measurements
- ✅ Three exercises
- ✅ AI feedback

### Version 2.0 (Planned)
- 🔄 More exercises (squats, lunges, push-ups)
- 🔄 Mobile app version
- 🔄 Voice coaching
- 🔄 Exercise programs
- 🔄 Progress analytics dashboard

### Version 3.0 (Future)
- 📅 Personalized exercise plans
- 📅 Remote physiotherapist consultation
- 📅 Multi-user support
- 📅 Cloud sync
- 📅 Wearable integration

---

## ⚠️ Disclaimer

This application is designed to assist with exercise form and provide feedback. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider before starting any new exercise program, especially if you have pre-existing conditions or injuries.

---

<div align="center">
  <br>
  <strong>Made with ❤️ for physiotherapy and rehabilitation</strong>
  <br>
  <br>
  <sub>© 2024 MediMotion. All rights reserved.</sub>
</div>
```

Now save, commit, and push:

```bash
cd /Users/nivetham/Documents/physiotherapy-app

# Save the README
# (The file is already created with the cat command above)

# Add to git
git add README.md

# Commit
git commit -m "Add comprehensive README.md with complete documentation"

# Push to GitHub
git push origin main
```

This README includes everything: features, installation, usage, troubleshooting, API documentation, and more. Just copy and paste the entire markdown code above into your `README.md` file! 📚
