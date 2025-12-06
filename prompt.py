prompt_template = """
You are an expert recruiter and HR analyst.
Your task is to evaluate the *content only* of a CV that will be provided as plain text.
Ignore layout, formatting, fonts, file type, and ATS parsing issues — evaluate strictly the textual information.

Input:
- CV content (plain text) → {cv}
- Job description → {job_description}

Evaluation Criteria (content-only):

1. Information completeness — /20
   Does the CV include essential sections (experience, education, skills)?
   Are responsibilities, dates, and job titles clearly described?

2. Professional experience depth & clarity — /25
   Are past roles clearly explained?
   Does the applicant describe what they *did* and *achieved*?
   Are achievements concrete, measurable, or action-oriented?

3. Skills relevance — /20
   - If job description is provided: how well do the skills match required skills/technologies?
   - If none: how well are the candidate's skills described (clarity, specificity, seniority)?

4. Writing quality — /15
   Clarity, conciseness, structure of sentences, absence of redundancy.

5. Consistency & coherence — /20
   Chronology makes sense, no contradictions, no obvious missing context.

Output Requirements:

For each criterion:
- Provide a sub-score.

Then:
- Compute the **total score /100**.
- If job description is provided, compute a **match percentage** based on skills, experience, and relevance.

Format the final answer in JSON:

```json
{{
  "completeness_score": 0,
  "experience_score": 0,
  "skills_score": 0,
  "writing_score": 0,
  "consistency_score": 0,
  "total_score": 0,
  "match_percentage": null,
}}
```

If the CV lacks enough information to evaluate a category, give a low score and explain why.
"""

cv = """
MOHAMED JBILOU
linkedin.com/in/mohamed-jbilou
github.com/Mohamed-Jbilou
Phone: +33 6 47 83 28 58
Email: mohamed.jbilou.pro@gmail.com
Address: 10 Rue des Iris, 75013 Paris, France
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
FINAL-YEAR PROJECT — “NEPTUNE”

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
GitHub: https://github.com/Mohamed-Jbilou
"""

job_description = """
Descriptif du poste

🌍 Qui sommes-nous ?

Safran.AI (anciennement Preligens) propose des solutions d'intelligence artificielle pour analyser les images satellite à haute résolution, les flux vidéos FMV (full motion video) et les signaux acoustiques. Nos solutions sont déployées au service de l'aéronautique, la défense et les applications gouvernementales.

La société développe depuis 2016 des algorithmes et logiciels complexes permettant d'analyser, de détecter et d'identifier automatiquement des objets présentant un intérêt militaire, à partir de données d'origine commerciale ou gouvernementale.

Depuis son intégration au groupe Safran en septembre 2024, Safran.AI contribue également à la transformation du groupe, en appliquant les solutions d'IA aux domaines de l'industrie 4.0. À titre d'exemple, l'analyse d'images automatisée par l'IA peut assister les contrôleurs en charge de l'inspection de pièces critiques en les aidant à détecter les anomalies éventuelles à partir de clichés numériques.

Chez Safran.AI, l'innovation et la création d'un monde plus sûr sont au cœur de notre ADN. En nous rejoignant, vous travaillerez avec des équipes passionnées et pluridisciplinaires (ingénieurs, chercheurs, développeurs…) parmi les plus talentueux du secteur, tous animés par une passion commune pour l'excellence technologique. Nous offrons un environnement de travail stimulant, où la créativité et la prise d'initiative sont encouragées, et où chaque idée compte.

😎 Votre mission, si vous l'acceptez

Vous rejoindrez l'équipe IA FMV qui développe les algorithmes de détection, classification et tracking d'objets sur des vidéos de drone (optique, infra-rouge…), dans le but d'enrichir des flux vidéo en temps réel.

En tant que stagiaire Deep Learning Scientist, votre périmètre comprendra, sans s'y limiter, les aspects suivants :

→ Développer, entraîner et tester les algorithmes de deep learning en utilisant nos outils d'IA.

 → Proposer de nouvelles idées pour améliorer les performances de nos algorithmes.

→ Comprendre et identifier les besoins et les attentes pour l'amélioration des algorithmes IA (quelles données sont nécessaires, quel point de fonctionnement est nécessaire, etc.) afin d'aider à planifier les nouveaux développements et définir les procédures de tests de performance.

 → Participer à la mise en place d'outils de ML Engineering, permettant à l'équipe de gagner en efficacité tout au long de la chaîne de d'entraînement (traitement des données, analyse des évaluations, packaging des modèles…)

🎯 Votre profil

→ Vous suivez une formation dans le domaine de la data science / du deep learning / de la computer vision et recherchez un stage de fin d'études.

 → Vous avez au moins une expérience pratique en computer vision / deep learning (stages, cours en ligne ou projets personnels).

 → Vous disposez de bonnes compétences en Python.

 → Vous avez de l'expérience dans la construction et l'entraînement de modèles de DL dans un cadre tel que Keras, TensorFlow ou PyTorch.

 → Vous êtes à l'aise dans un environnement UNIX/Linux.

→ Vous avez une appétence et des notions concernant les bonnes pratiques de développement logiciels.

 → Vous faites preuve de bonnes capacités de communication et de travail en équipe, et avez un esprit rigoureux, créatif et méticuleux.

 → Vous avez la volonté de relever des défis, de faire preuve de résilience et de toujours apprendre de nouvelles compétences.

 → Vous avez une appétence la mise en œuvre d'outils de ML Engineering et de pratiques visant d'accroître l'efficacité de nos process.

Si vous ne remplissez pas 100% des critères ci-dessus, pas de panique, vous pouvez nous indiquer les raisons pour lesquelles vous pensez tout de même être un bon candidat pour ce rôle !
"""