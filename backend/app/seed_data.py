"""Seed content for PySchool: 10 depth categories + 100 learning paths."""

CATEGORIES = [
    ("Surface (sabko pata hai)", "🌊", "Surface", 1),
    ("Just Below Surface", "🌊", "Below Surface", 2),
    ("Mid-Level Tech", "🌊", "Mid-Level", 3),
    ("Getting Deeper - Scientific", "🌊🌊", "Scientific", 4),
    ("Finance / Business", "🌊🌊", "Finance", 5),
    ("Infra / Systems", "🌊🌊", "Infra", 6),
    ("AI Frontier", "🌊🌊", "AI Frontier", 7),
    ("Deep - Research Grade", "🌊🌊🌊", "Research", 8),
    ("Abyss - System/Language Level", "🌊🌊🌊", "Abyss", 9),
    ("AGI / General Reasoning", "🤖", "Frontier", 10),
]

# (category_idx, name, description, libraries, slug, difficulty 1-5)
PATHS = [
    # --- Surface (1) ---
    (1, "Web Development", "Build websites & web apps with Python frameworks", "Django, Flask, FastAPI", "web-dev", 2),
    (1, "Data Science / Analysis", "Analyze data, find insights, make charts", "Pandas, NumPy", "data-science", 2),
    (1, "Automation / Scripting", "Automate boring repetitive tasks with scripts", "Schedule, OS, Pathlib", "automation", 1),
    (1, "Machine Learning", "Teach computers to learn from data", "scikit-learn", "machine-learning", 3),
    (1, "Web Scraping", "Extract data from websites automatically", "BeautifulSoup, Scrapy", "web-scraping", 2),
    (1, "Game Development", "Make 2D games in Python", "Pygame", "game-dev", 2),
    (1, "GUI Applications", "Desktop apps with buttons, windows, forms", "Tkinter, PyQt", "gui-apps", 2),
    (1, "API Building", "Design and build REST APIs", "FastAPI, Django REST", "api-building", 2),
    (1, "Chatbots", "Build chat assistants and bots", "ChatterBot, Rasa", "chatbots", 2),
    (1, "Excel Automation", "Read/write Excel files programmatically", "openpyxl, pandas", "excel-automation", 1),

    # --- Below Surface (2) ---
    (2, "Deep Learning", "Neural networks that learn complex patterns", "PyTorch, TensorFlow", "deep-learning", 4),
    (2, "Computer Vision", "Teach computers to see and understand images", "OpenCV, torchvision", "computer-vision", 4),
    (2, "NLP (Natural Language Processing)", "Process and understand human language", "spaCy, NLTK, transformers", "nlp", 4),
    (2, "Data Visualization", "Turn data into beautiful interactive charts", "Matplotlib, Plotly, Seaborn", "data-viz", 2),
    (2, "Cloud Computing", "Deploy apps and use AWS from Python", "boto3", "cloud-computing", 3),
    (2, "DevOps Scripting", "Script infrastructure and deployment pipelines", "Fabric, Python+Docker", "devops-scripting", 3),
    (2, "Testing / QA Automation", "Automated testing of software", "pytest, Selenium", "testing-qa", 2),
    (2, "Database Operations", "Work with databases from Python", "SQLAlchemy, psycopg", "database-ops", 2),
    (2, "ETL Pipelines", "Extract, Transform, Load data pipelines", "Pandas, Airflow", "etl-pipelines", 3),
    (2, "Recommendation Systems", "Suggest products/content users will love", "Surprise, implicit", "recommendation-systems", 4),

    # --- Mid-Level (3) ---
    (3, "Reinforcement Learning", "Agents that learn by trial and error", "Gymnasium, Stable-Baselines3", "reinforcement-learning", 5),
    (3, "Generative AI / LLM Fine-tuning", "Customize large language models", "HuggingFace, LoRA", "genai-finetuning", 5),
    (3, "Time Series Forecasting", "Predict future values from historical data", "Prophet, statsmodels", "time-series", 4),
    (3, "Computer Graphics / Animation", "Programmatic animation and visual math", "Manim, Blender scripting", "cgi-animation", 4),
    (3, "Cybersecurity / Pentesting", "Find and exploit security vulnerabilities", "Scapy, pwntools", "cybersecurity", 4),
    (3, "Network Programming", "Build apps that talk over networks", "sockets, aiohttp", "network-programming", 3),
    (3, "Cryptography Implementation", "Encrypt, sign and secure data", "cryptography, PyCryptodome", "cryptography", 4),
    (3, "Blockchain Scripting", "Interact with blockchains and smart contracts", "web3.py", "blockchain", 4),
    (3, "IoT Programming", "Program microcontrollers and sensors", "MicroPython, RPi.GPIO", "iot", 3),
    (3, "Robotics", "Control robots with Python", "ROS, PyRobot", "robotics", 5),
    (3, "Drone Programming", "Autonomous drone flight control", "MAVSDK, DroneKit", "drones", 5),
    (3, "Audio Processing", "Analyze and transform sound", "librosa, pydub", "audio-processing", 4),
    (3, "Video Processing", "Edit and analyze video programmatically", "moviepy, opencv", "video-processing", 3),
    (3, "Image Generation", "Generate images with diffusion models", "diffusers, stable-diffusion", "image-generation", 5),
    (3, "Speech Recognition / Synthesis", "Voice input and speech output", "whisper, pyttsx3", "speech", 4),

    # --- Scientific (4) ---
    (4, "Bioinformatics", "Analyze biological and genetic data", "Biopython", "bioinformatics", 5),
    (4, "Computational Chemistry", "Simulate molecules and reactions", "RDKit, ASE", "comp-chemistry", 5),
    (4, "Physics Simulations", "Model physical systems numerically", "NumPy, SciPy", "physics-sims", 4),
    (4, "Astronomy Data", "Analyze astronomical observations", "Astropy", "astronomy", 5),
    (4, "Geospatial / GIS", "Map and analyze geographic data", "GeoPandas, Folium", "gis", 4),
    (4, "Climate Modeling", "Model weather and climate systems", "xarray, netCDF4", "climate-modeling", 5),
    (4, "Quantum Computing", "Program quantum algorithms", "Qiskit", "quantum-computing", 5),
    (4, "Numerical Methods", "High-precision math and simulation", "SciPy, NumPy", "numerical-methods", 4),
    (4, "Finite Element Analysis", "Structural and thermal simulation", "FEniCS, PyFEM", "fea", 5),
    (4, "Fluid Dynamics Simulation", "Simulate liquids and gases", "FEniCS, PyFR", "fluid-dynamics", 5),

    # --- Finance (5) ---
    (5, "Algorithmic Trading", "Automated trading strategies", "ccxt, backtrader", "algo-trading", 4),
    (5, "Quantitative Finance", "Math + finance for pricing and analysis", "NumPy, QuantLib", "quant-finance", 5),
    (5, "Risk Modeling", "Measure and manage financial risk", "VaR, pyfolio", "risk-modeling", 5),
    (5, "Fraud Detection Systems", "Detect fraudulent transactions with ML", "scikit-learn, imbalanced-learn", "fraud-detection", 4),
    (5, "Credit Scoring Models", "ML models that score borrowers", "XGBoost, OptBinning", "credit-scoring", 4),
    (5, "Portfolio Optimization", "Optimize investment portfolios", "PyPortfolioOpt", "portfolio-optimization", 4),
    (5, "Crypto Trading Bots", "Automated crypto trading systems", "ccxt, web3", "crypto-bots", 4),
    (5, "Financial Data Pipelines", "Streams of market data for analysis", "pandas, kafka-python", "financial-pipelines", 4),

    # --- Infra (6) ---
    (6, "Distributed Systems", "Parallel computing across many machines", "Celery, Ray", "distributed-systems", 5),
    (6, "Microservices Architecture", "Many small services working together", "FastAPI, Docker", "microservices", 4),
    (6, "Container Orchestration", "Manage Kubernetes clusters with Python", "k8s operators, kubernetes client", "container-orchestration", 5),
    (6, "Message Queues", "Async messaging between services", "Kafka, RabbitMQ", "message-queues", 4),
    (6, "Load Testing", "Stress-test web apps under traffic", "Locust", "load-testing", 3),
    (6, "Monitoring / Observability", "Track system health and metrics", "Prometheus, Grafana", "monitoring", 3),
    (6, "CI/CD Pipeline Scripting", "Automate build, test, deploy", "GitHub Actions, Jenkins", "cicd", 3),
    (6, "Package / Library Development", "Build and publish your own PyPI package", "setuptools, hatch", "package-dev", 3),
    (6, "Compiler / Interpreter Building", "Write a mini language in Python", "ply, ast", "compiler-building", 5),

    # --- AI Frontier (7) ---
    (7, "Multi-Agent Systems", "Multiple AI agents collaborating", "LangGraph, AutoGen", "multi-agent", 5),
    (7, "AI Agents with Tool-Use", "Agents that call functions and tools", "OpenAI, LangChain", "ai-agents", 5),
    (7, "RAG Systems", "Retrieval-Augmented Generation pipelines", "LangChain, LlamaIndex", "rag", 5),
    (7, "Vector Databases", "Store and search embeddings", "Pinecone, ChromaDB", "vector-db", 4),
    (7, "Fine-tuning LLMs", "LoRA & QLoRA model customization", "PEFT, transformers", "llm-finetuning", 5),
    (7, "Model Quantization / Optimization", "Make models small and fast", "ONNX, bitsandbytes", "quantization", 5),
    (7, "MLOps", "Deploy and monitor ML models in production", "MLflow, Kubeflow", "mlops", 4),
    (7, "Federated Learning", "Train across devices without centralizing data", "Flower", "federated-learning", 5),
    (7, "Explainable AI", "Understand why models make decisions", "SHAP, LIME", "xai", 4),
    (7, "Synthetic Data Generation", "Create realistic fake data for ML", "Faker, SDV", "synthetic-data", 4),
    (7, "AI Safety / Alignment", "Research tooling for safe AI", "interpretability libs", "ai-safety", 5),
    (7, "Prompt Engineering Frameworks", "Systematic prompt development", "LangChain, DSPy", "prompt-eng", 4),
    (7, "Voice Cloning / Synthesis", "Clone and synthesize speech", "Coqui TTS, RVC", "voice-cloning", 5),
    (7, "Emotion Detection", "Detect emotion from voice and text", "transformers, librosa", "emotion-detection", 4),

    # --- Research (8) ---
    (8, "Genomics / DNA Analysis", "DNA sequence analysis pipelines", "Biopython, pysam", "genomics", 5),
    (8, "Drug Discovery", "Molecular modeling for medicine", "RDKit, DeepChem", "drug-discovery", 5),
    (8, "Neuroscience Data Analysis", "EEG / fMRI signal analysis", "MNE, Nilearn", "neuroscience", 5),
    (8, "Medical Imaging", "Radiology AI with deep learning", "MONAI, SimpleITK", "medical-imaging", 5),
    (8, "Epidemiology Modeling", "Model disease spread", "EpiModel, SciPy", "epidemiology", 5),
    (8, "Materials Science Simulation", "Simulate materials at atomic scale", "ASE, pymatgen", "materials-science", 5),
    (8, "Weather Prediction Models", "Numerical weather forecasting", "xarray, WRF", "weather-prediction", 5),
    (8, "Autonomous Vehicle Perception", "Self-driving car sensor perception", "OpenCV, ultralytics YOLO", "autonomous-driving", 5),
    (8, "SLAM / Localization", "Robot mapping and position tracking", "slam-toolbox, g2o", "slam", 5),
    (8, "Satellite Image Analysis", "Analyze earth observation imagery", "rasterio, GDAL", "satellite-imagery", 5),

    # --- Abyss (9) ---
    (9, "Python C-Extensions", "Speed up Python with C via Cython/ctypes", "Cython, ctypes", "c-extensions", 5),
    (9, "Build Your Own ML Framework", "Neural networks from scratch", "NumPy only", "own-ml-framework", 5),
    (9, "GPU Programming", "CUDA from Python for massive speedup", "Numba, CuPy", "gpu-programming", 5),
    (9, "Parallel / Distributed Computing", "MPI for multi-node computing", "MPI4py, Dask", "parallel-computing", 5),
    (9, "OS Scripting / Tooling", "System-level automation and tools", "psutil, ctypes", "os-tooling", 4),
    (9, "Malware Analysis / Reverse Engineering", "Analyze and reverse malicious code", "capstone, pefile", "malware-analysis", 5),
    (9, "Digital Forensics Tooling", "Investigate digital evidence", "sleuthkit, pytsk3", "forensics", 5),
    (9, "Embedded Systems Firmware", "Firmware helpers and flashing tools", "pyserial, esptool", "embedded-firmware", 4),
    (9, "Simulation Engines", "Physics engines from scratch", "NumPy, pygame", "simulation-engines", 5),
    (9, "Build Your Own Database Engine", "Storage, indexing, queries from scratch", "pure Python/SQLite internals", "own-db-engine", 5),
    (9, "Build Your Own Web Framework", "Like Django — but you build the framework", "pure Python", "own-web-framework", 5),
    (9, "Search Engine Building", "Indexing + ranking algorithms", "whoosh, pure Python", "search-engine", 5),
    (9, "Programming Language / DSL", "Design a language and compiler in Python", "ply, lark", "own-language", 5),

    # --- AGI (10) ---
    (10, "AGI / General Reasoning Research", "Frontier-level general AI research", "PyTorch, transformers", "agi-research", 5),
]

# Level assessment questions per path — each path gets 5 adaptive questions.
# To keep seed compact, we generate generic-but-solid basics questions,
# plus path-flavoured questions for the first 6 flagship paths.
ASSESSMENT_BASE = [
    (
        "What is a variable in Python?",
        "A container that stores data", "A type of loop", "A function name", "An imported module",
        "A", 1,
    ),
    (
        "Which keyword defines a function in Python?",
        "func", "def", "function", "define",
        "B", 1,
    ),
    (
        "What does len() do?",
        "Runs code twice", "Converts to integer", "Returns the length of a sequence", "Deletes a variable",
        "C", 1,
    ),
    (
        "What data structure stores key-value pairs?",
        "List", "Tuple", "Set", "Dictionary",
        "D", 1,
    ),
    (
        "What will [x for x in range(5)] produce?",
        "[0,1,2,3,4]", "[1,2,3,4,5]", "[5]", "Error",
        "A", 2,
    ),
    (
        "Which is correct exception handling syntax?",
        "catch:", "try/except", "handle:", "error:",
        "B", 2,
    ),
    (
        "What is a decorator?",
        "A function that modifies another function", "A type of loop", "A variable type", "A list method",
        "A", 3,
    ),
    (
        "What is a generator?",
        "A function that yields values lazily", "A loop", "A module", "A database",
        "A", 3,
    ),
    (
        "Which of these is a lambda?",
        "x = lambda a: a + 1", "x = def(a)", "x = func(a)", "x = function(a)",
        "A", 3,
    ),
    (
        "What does *args mean in a function signature?",
        "Positional arguments packed into a tuple", "Keyword args", "No args allowed", "Only numbers",
        "A", 4,
    ),
]

# Flagship paths (first 6) get path-specific extra questions.
PATH_FLAGSHIP_QUESTIONS = {
    "data-science": [
        (
            "Which library is best for tabular data manipulation?",
            "Pandas", "Pygame", "Scapy", "Qiskit",
            "A", 2,
        ),
        (
            "How do you load a CSV with pandas?",
            "pd.read_csv('file.csv')", "csv.load()", "open().csv()", "pd.csv('file')",
            "A", 1,
        ),
        (
            "What does df.dropna() do?",
            "Removes rows with missing values", "Adds NaN values", "Sorts the dataframe", "Renames columns",
            "A", 2,
        ),
    ],
    "machine-learning": [
        (
            "What is overfitting?",
            "Model memorizes training data too well", "Model is too fast", "Model has no data", "Model is a web server",
            "A", 2,
        ),
        (
            "Which library provides train_test_split?",
            "scikit-learn", "Flask", "PyQt", "Scapy",
            "A", 1,
        ),
        (
            "What does accuracy measure?",
            "Correct predictions / total predictions", "Loss squared", "Gradient size", "Data size",
            "A", 1,
        ),
    ],
    "web-dev": [
        (
            "Which framework is best for building fast APIs?",
            "FastAPI", "Pygame", "Tkinter", "Scrapy",
            "A", 1,
        ),
        (
            "What does a route decorator do in FastAPI?",
            "Maps a URL to a function", "Creates a database", "Renders images", "Compiles code",
            "A", 1,
        ),
        (
            "What is a REST API?",
            "Web interface using HTTP methods", "A desktop app", "A database", "A Python library",
            "A", 2,
        ),
    ],
    "automation": [
        (
            "Which module schedules tasks to run periodically?",
            "schedule", "pygame", "numpy", "folium",
            "A", 2,
        ),
        (
            "How do you get the current working directory?",
            "os.getcwd()", "os.chdir()", "os.listdir()", "os.remove()",
            "A", 1,
        ),
        (
            "Which library copies files easily?",
            "shutil", "socket", "tkinter", "matplotlib",
            "A", 1,
        ),
    ],
    "web-scraping": [
        (
            "Which library parses HTML for scraping?",
            "BeautifulSoup", "NumPy", "Pygame", "Qiskit",
            "A", 1,
        ),
        (
            "What method sends a GET request in requests?",
            "requests.get()", "requests.post()", "requests.delete()", "requests.head()",
            "A", 1,
        ),
        (
            "What is a User-Agent?",
            "A string identifying the client browser", "A database", "A CSS file", "A cookie",
            "A", 3,
        ),
    ],
    "chatbots": [
        (
            "What is an intents file in chatbot training?",
            "A structured list of user intentions", "A JSON of colors", "An image file", "A database index",
            "A", 2,
        ),
        (
            "Which library helps build conversational agents?",
            "Rasa", "Pygame", "Qiskit", "Matplotlib",
            "A", 2,
        ),
        (
            "What is a webhook for a bot?",
            "URL that receives bot events", "A type of loop", "A CSS class", "An antivirus",
            "A", 3,
        ),
    ],
}

# Preview lessons: full Day-1 lesson for flagship paths, first lesson for others.
LESSON_TEMPLATES = {
    "data-science": [
        ("Welcome to Data Science with Python",
         "Today you start your journey into Data Science.\n\n"
         "**What you'll learn:**\n"
         "- What data science is and what a data scientist does\n"
         "- How to set up your Python environment\n"
         "- First steps with Pandas — the #1 data library\n\n"
         "**Theory**\n"
         "Data Science = collecting data, cleaning it, analyzing it, and telling a story with it.\n"
         "The core tool is **Pandas**, which gives us `DataFrame` — a spreadsheet-like structure in Python.\n\n"
         "**Day 1 Goal:** Load your first dataset and print a summary of it.",
         "import pandas as pd\n\n"
         "# Create a small dataset of student scores\n"
         "data = {\n"
         "    'name': ['Aarav', 'Riya', 'Kabir', 'Anya'],\n"
         "    'python_score': [85, 92, 78, 95],\n"
         "    'math_score': [88, 79, 91, 84],\n"
         "}\n\n"
         "df = pd.DataFrame(data)\n"
         "print(df)\n"
         "print('---')\n"
         "print(df.describe())",
         ["What library is king for data analysis?", "What structure does Pandas use to hold tabular data?", "Which method prints statistical summary of a DataFrame?"],
         ["Pandas", "DataFrame", "df.describe()"],
         "Create your own DataFrame with 5 rows (favourite movies + rating) and print df.describe(). Run it and note what you see."),
    ],
    "machine-learning": [
        ("Welcome to Machine Learning with Python",
         "**What you'll learn:**\n"
         "- The 3 types of ML: supervised, unsupervised, reinforcement\n"
         "- What features and labels mean\n"
         "- Your first ML model with scikit-learn\n\n"
         "**Theory**\n"
         "Machine Learning = teaching a computer to find patterns in data.\n"
         "In **supervised learning** we give the model examples with answers (labels), and it learns.\n"
         "scikit-learn is the beginner-friendly ML library.",
         "from sklearn.datasets import load_iris\n"
         "from sklearn.model_selection import train_test_split\n"
         "from sklearn.tree import DecisionTreeClassifier\n"
         "from sklearn.metrics import accuracy_score\n\n"
         "# Load the famous iris flower dataset\n"
         "data = load_iris()\n"
         "X_train, X_test, y_train, y_test = train_test_split(\n"
         "    data.data, data.target, test_size=0.2, random_state=42\n"
         ")\n\n"
         "model = DecisionTreeClassifier()\n"
         "model.fit(X_train, y_train)\n"
         "predictions = model.predict(X_test)\n"
         "print('Accuracy:', accuracy_score(y_test, predictions))",
         ["What are the 3 types of ML?", "Which library is a beginner-friendly ML toolkit?", "What does train_test_split do?"],
         ["Supervised, unsupervised, reinforcement", "scikit-learn", "Splits data into training and testing sets"],
         "Train the same model without setting random_state. What changes? Run it 3 times and observe."),
    ],
    "web-dev": [
        ("Welcome to Web Development with Python",
         "**What you'll learn:**\n"
         "- Client vs server\n"
         "- What a web framework does\n"
         "- Build your first FastAPI endpoint\n\n"
         "**Theory**\n"
         "The **backend** runs on a server and sends data to the browser (client).\n"
         "FastAPI is a modern framework to build APIs quickly. An **API endpoint** is a URL that returns data.",
         "from fastapi import FastAPI\n\n"
         "app = FastAPI()\n\n"
         "@app.get('/')\n"
         "def home():\n"
         "    return {'message': 'Hello PySchool!'}\n\n"
         "@app.get('/greet/{name}')\n"
         "def greet(name: str):\n"
         "    return {'hello': name}",
         ["What runs on the server: backend or frontend?", "What does an endpoint return?", "Which framework did we use today?"],
         ["Backend", "Data (usually JSON)", "FastAPI"],
         "Add a new endpoint /square/{number} that returns the square of the number."),
    ],
    "automation": [
        ("Welcome to Automation with Python",
         "**What you'll learn:**\n"
         "- Why automation is powerful\n"
         "- Working with files and folders\n"
         "- Renaming 100 files in 3 lines\n\n"
         "**Theory**\n"
         "Automation = writing a script that does boring work for you.\n"
         "Python's `os` and `shutil` modules let you control files, folders, and the OS.",
         "import os\n"
         "import shutil\n\n"
         "# Make a folder structure\n"
         "os.makedirs('projects', exist_ok=True)\n\n"
         "# List all files in current directory\n"
         "for f in os.listdir('.'):\n"
         "    print(f)\n\n"
         "# Copy a file\n"
         "shutil.copy('notes.txt', 'projects/notes_backup.txt')",
         ["Which module controls files/folders?", "Which module copies files easily?", "What does os.makedirs do?"],
         ["os", "shutil", "Creates a directory (including parents with exist_ok=True)"],
         "Create a script that renames all .txt files in a folder to add the date prefix (e.g. 2026-08-08_notes.txt)."),
    ],
    "web-scraping": [
        ("Welcome to Web Scraping with Python",
         "**What you'll learn:**\n"
         "- How scraping works (and is legal/ethical)\n"
         "- Fetching pages with requests\n"
         "- Parsing with BeautifulSoup\n\n"
         "**Theory**\n"
         "Web scraping = fetching a webpage and extracting data from its HTML.\n"
         "`requests` downloads the page, `BeautifulSoup` helps find the data you want.",
         "import requests\n"
         "from bs4 import BeautifulSoup\n\n"
         "# Fetch a page\n"
         "response = requests.get('https://example.com')\n"
         "soup = BeautifulSoup(response.text, 'html.parser')\n\n"
         "# Extract the main heading\n"
         "print(soup.find('h1').text)",
         ["Which library downloads web pages?", "Which library parses HTML?", "What is one ethical rule of scraping?"],
         ["requests", "BeautifulSoup", "Don't overload servers; check robots.txt and respect terms of service"],
         "Fetch your favourite news site, list all <h2> headlines, and print them."),
    ],
    "chatbots": [
        ("Welcome to Chatbot Building",
         "**What you'll learn:**\n"
         "- Rule-based vs AI chatbots\n"
         "- Intents, entities, responses\n"
         "- Build a simple rule-based bot\n\n"
         "**Theory**\n"
         "A chatbot needs to understand user input and reply.\n"
         "A **rule-based bot** matches patterns with `if/else`. An **AI bot** learns from conversations.",
         "# Simple rule-based assistant\n"
         "responses = {\n"
         "    'hi': 'Hello! How can I help you today?',\n"
         "    'name': 'I am PyBot, your Python study assistant.',\n"
         "    'bye': 'Goodbye! Keep learning Python!' \n"
         "}\n\n"
         "def chat(message):\n"
         "    message = message.lower()\n"
         "    for key, reply in responses.items():\n"
         "        if key in message:\n"
         "            return reply\n"
         "    return 'Sorry, I did not understand.'\n\n"
         "print(chat('Hi there'))\n"
         "print(chat('What is your name?'))",
         ["What are the two types of chatbots?", "What is an intent?", "What does .lower() do?"],
         ["Rule-based and AI/ML-based", "The user's goal/purpose behind a message", "Converts the string to lowercase for matching"],
         "Add 5 new intents and responses to the bot, then test each one."),
    ],
}
