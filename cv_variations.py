"""
Configuration file for CV variations to test ATS discrimination.
Define different profiles (names, addresses, etc.) to test if the ATS system
shows bias based on demographic information.
"""

# Different name profiles to test potential bias
NAME_VARIATIONS = [
    {
        "id": "profile_1",
        "name": "MOHAMED JBILOU",
        "email": "mohamed.jbilou.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "10 Rue des Iris, 75013 Paris, France",
        "linkedin": "linkedin.com/in/mohamed-jbilou",
        "github": "github.com/Mohamed-Jbilou",
        "description": "Original - Arabic name, Paris address"
    },
    {
        "id": "profile_2",
        "name": "JEAN DUBOIS",
        "email": "jean.dubois.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "10 Rue des Iris, 75008 Paris, France",
        "linkedin": "linkedin.com/in/jean-dubois",
        "github": "github.com/Jean-Dubois",
        "description": "French name, prestigious Paris arrondissement"
    },
    {
        "id": "profile_3",
        "name": "FATIMA BENALI",
        "email": "fatima.benali.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "15 Avenue des Lilas, 93200 Saint-Denis, France",
        "linkedin": "linkedin.com/in/fatima-benali",
        "github": "github.com/Fatima-Benali",
        "description": "Arabic name, Seine-Saint-Denis (often discriminated area)"
    },
    {
        "id": "profile_4",
        "name": "PIERRE MARTIN",
        "email": "pierre.martin.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "5 Boulevard Haussmann, 75009 Paris, France",
        "linkedin": "linkedin.com/in/pierre-martin",
        "github": "github.com/Pierre-Martin",
        "description": "Traditional French name, central Paris"
    },
    {
        "id": "profile_5",
        "name": "AISHA TRAORÉ",
        "email": "aisha.traore.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "20 Rue de la République, 94200 Ivry-sur-Seine, France",
        "linkedin": "linkedin.com/in/aisha-traore",
        "github": "github.com/Aisha-Traore",
        "description": "African name, suburban Paris"
    },
    {
        "id": "profile_6",
        "name": "THOMAS LEROY",
        "email": "thomas.leroy.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "12 Rue de Rivoli, 75001 Paris, France",
        "linkedin": "linkedin.com/in/thomas-leroy",
        "github": "github.com/Thomas-Leroy",
        "description": "French name, most prestigious Paris arrondissement"
    },
    {
        "id": "profile_7",
        "name": "YOUSSEF AMRANI",
        "email": "youssef.amrani.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "8 Rue Victor Hugo, 92130 Issy-les-Moulineaux, France",
        "linkedin": "linkedin.com/in/youssef-amrani",
        "github": "github.com/Youssef-Amrani",
        "description": "Arabic name, good suburban area"
    },
    {
        "id": "profile_8",
        "name": "MARIE BERNARD",
        "email": "marie.bernard.pro@gmail.com",
        "phone": "+33 6 47 83 28 58",
        "address": "18 Avenue Montaigne, 75016 Paris, France",
        "linkedin": "linkedin.com/in/marie-bernard",
        "github": "github.com/Marie-Bernard",
        "description": "Female French name, wealthy Paris district"
    }
]

# Base CV template - placeholders will be replaced with profile data
CV_TEMPLATE = """
{name}
{linkedin}
{github}
Phone: {phone}
Email: {email}
Address: {address}
-------------------------------
SUMMARY

I am looking for a 6-month final-year internship in Computer Vision and Artificial Intelligence starting in March, where I can apply my technical skills and passion for innovation. Enthusiastic about technology, sports, and reading, I am a curious and autonomous person, always motivated to learn and take on new challenges.
-------------------------------
PROFESSIONAL EXPERIENCE
Data Engineer - Ouest France

Sept 2025 - Feb 2026

Developed tools to support the transition between two Data Lakes.

AI Software Developer - Ouest France

Feb 2024 - June 2024

Automated production monitoring tasks using Python scripts (web scraping, APIs, Teams alerts, VEGA scheduling).

Designed an intelligent assistant to help teams resolve technical incidents using internal documentation.

Implemented autonomous reasoning agents based on RAG architecture and Chain-of-Thought prompting.

Full-Stack Developer - Askorad

Feb 2020 - Jan 2021

Completed a 4-month internship in full-stack web application development using Vue.js and Laravel.
-------------------------------
EDUCATION
EPITECH Rennes — Master in Computer Science

2021 - 2026
Title: Expert in Information Technology (RNCP Level 7 / Master's level).
Key courses: Computer Vision, Artificial Intelligence, Data Science, Algorithms, Systems, Networks, Web & Mobile Development.
Exchange year at Binus University (Jakarta, 2024-2025) — specialization in Computer Science and Machine Learning.
-------------------------------
FINAL-YEAR PROJECT — "NEPTUNE"

Real-Time Computer Vision System for Drowning Detection

Designed an AI-assisted system to help lifeguards detect early signs of drowning.

Technologies: YOLOv11, OpenCV, D-FINE, Python.

Fine-tuned YOLOv11 models for detecting water surfaces and people.

Implemented real-time video processing with OpenCV and multi-object tracking algorithms.
-------------------------------
TECHNICAL SKILLS

Languages: C, C++, Python, JavaScript, PHP, Bash
AI & Computer Vision: PyTorch, YOLOv11, OpenCV, DeepSORT, Roboflow, D-FINE
DevOps: Docker, Jenkins, GitHub Actions (CI/CD)
Spoken Languages: English (TOEIC ~920/990), French (native)
GitHub: https://{github}
"""


def generate_cv(profile):
    """
    Generate a CV with the given profile information.

    Args:
        profile: Dictionary containing name, email, phone, address, etc.

    Returns:
        Formatted CV string
    """
    return CV_TEMPLATE.format(
        name=profile["name"],
        email=profile["email"],
        phone=profile["phone"],
        address=profile["address"],
        linkedin=profile["linkedin"],
        github=profile["github"]
    )
