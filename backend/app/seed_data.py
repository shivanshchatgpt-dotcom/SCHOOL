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
    (10, "Python for AI Research", "Start from zero and build the Python foundations behind AI research", "Python, NumPy, PyTorch", "agi-research", 4),
]

# The catalog is intentionally broad; these are the only tracks with an authored
# curriculum in this MVP. The rest remain visible as future tracks, not as fake courses.
LAUNCH_PATH_SLUGS = {"agi-research", "data-science", "web-dev"}


def _foundation_curriculum(focus: str, capstone: str):
    """Fourteen authored, zero-to-code foundation milestones for a launch track."""
    lessons = [
        ("Your first Python program", "Python foundations", "Explain what a program is and use print() to communicate with the computer.", "name = 'PySchool learner'\nprint('Hello, ' + name)\nprint('I am starting ' + '" + focus + "')", "Write a three-line introduction program that prints your name and your learning goal.", ["print("], "A program can store text and send output with print()."),
        ("Variables and values", "Python foundations", "Store numbers and text in variables, then use them in an expression.", "hours_per_day = 1\ndays = 14\nprint('Foundation hours:', hours_per_day * days)", "Create variables for your daily study hours and course days, then print the total hours.", ["=", "print("], "Variables give meaningful names to values so code is easier to read."),
        ("Numbers, strings and input", "Python foundations", "Tell apart numeric and text values and collect a simple input.", "student = input('Your name: ')\nprint('Welcome, ' + student)\nprint('You can learn step by step.')", "Ask for a learner's name and favourite subject, then print a welcome message.", ["input(", "print("], "input() returns text, so combine it carefully with other strings."),
        ("Making decisions with if", "Python foundations", "Use a comparison and if/else to choose an outcome.", "score = 72\nif score >= 60:\n    print('Milestone passed')\nelse:\n    print('Review and try again')", "Write a program that prints whether a score is passing (60 or above).", ["if ", "else", "print("], "A condition lets one program respond differently to different data."),
        ("Repeating work with loops", "Python foundations", "Use a for loop to repeat a task without copying code.", "for day in range(1, 6):\n    print('Study day', day)\nprint('Consistency compounds.')", "Use a for loop to print a five-day study plan.", ["for ", "range(", "print("], "Loops are useful when the same action follows a pattern."),
        ("Lists: a collection of values", "Python foundations", "Create a list, access its values and loop through it.", "topics = ['Python', 'logic', 'practice']\nfor topic in topics:\n    print('Today:', topic)", "Make a list of three topics you want to learn and print every item with a loop.", ["[", "for ", "print("], "Lists keep related values together in one ordered collection."),
        ("Functions: reusable instructions", "Python foundations", "Define a function with a parameter and call it.", "def encourage(name):\n    print('Keep going, ' + name + '!')\n\nencourage('Aarav')", "Write a function called greet that accepts a name and prints a greeting.", ["def ", "print("], "Functions package a useful action so it can be reused and tested."),
        ("Return values and small calculations", "Python foundations", "Return a result from a function instead of only printing it.", "def study_total(hours, days):\n    return hours * days\n\nprint(study_total(1, 14))", "Write a function that returns the square of a number and print its result.", ["def ", "return", "print("], "return sends a value back to the caller for later use."),
        ("Dictionaries: label your data", "Python foundations", "Represent labelled information with a dictionary.", "student = {'name': 'Riya', 'streak': 4}\nprint(student['name'])\nprint(student['streak'])", "Create a dictionary for a student with name and goal, then print both values.", ["{", "print("], "Dictionaries map meaningful keys to values."),
        ("Debugging and exceptions", "Programming practice", "Read an error, use try/except, and give a helpful fallback message.", "try:\n    age = int('not a number')\nexcept ValueError:\n    print('Please enter a whole number')", "Use try/except around an int conversion and print a helpful error message.", ["try:", "except", "print("], "Errors are information: isolate the risky line and explain what the user can do."),
        ("Files and structured data", "Programming practice", "Write simple text to a file using a context manager.", "with open('study_log.txt', 'w') as file:\n    file.write('Day 11: practiced Python\\n')\nprint('Log saved')", "Write a one-line study log to a text file and print a confirmation.", ["with open(", "write(", "print("], "with closes a file safely even when something goes wrong."),
        ("Testing your own code", "Software engineering", "Use assert to check an expected result.", "def add(a, b):\n    return a + b\n\nassert add(2, 3) == 5\nprint('Test passed')", "Write one small function and an assert that proves it works for one example.", ["def ", "assert ", "print("], "A tiny automated check protects a function when you change it later."),
        ("Problem decomposition", "Computational thinking", "Break a real problem into input, processing and output steps.", "def plan_task(task):\n    steps = ['understand', 'build', 'check']\n    for step in steps:\n        print(step, task)\n\nplan_task('my project')", "Create a function that prints at least three steps for completing a task.", ["def ", "for ", "print("], "Good programs start as small, testable steps before they become big projects."),
        ("Foundation capstone", focus, "Combine variables, a function, a collection and a loop in a small working program.", "def show_progress(days):\n    for day in days:\n        print('Completed day', day)\n\ncompleted = [1, 2, 3]\nshow_progress(completed)\nprint('Ready for the next module')", capstone, ["def ", "for ", "print("], "This capstone is evidence that you can combine the core building blocks of Python."),
    ]
    return lessons


CURRICULA = {
    "agi-research": _foundation_curriculum(
        "AI Research",
        "Build a mini experiment log: store three experiment names in a list, write a function that prints each experiment, and print a final conclusion.",
    ),
    "data-science": _foundation_curriculum(
        "Data Science",
        "Build a mini study-data report: store three scores in a list, write a function that prints each score, and print a final summary line.",
    ),
    "web-dev": _foundation_curriculum(
        "Web Development",
        "Build a mini profile generator: store three page sections in a list, write a function that prints each section, and print a final page-ready message.",
    ),
}

# The first fourteen lessons above are deliberately written line-by-line.  The
# rest of each programme is a 180-day syllabus made from named, teachable daily
# milestones—not a claim that a fourteen-day introduction is the whole school.
def _topics(value: str) -> list[str]:
    return value.split("|")


COMMON_180_PHASES = [
    ("Core Python", "Python foundations", "Build reliable Python programs with control flow and collections.", _topics("Boolean values|Comparisons|elif decision trees|Nested conditions|while loops|Loop control|String indexing|String methods|List methods|Tuples and unpacking|Sets|Dictionary methods|Function parameters|Return values|Variable scope")),
    ("Practical Python", "Programming practice", "Turn core syntax into small programs and learn to debug them.", _topics("Modules and imports|Standard library tour|Command-line arguments|Input validation|Exceptions|Custom exceptions|Reading text files|Writing CSV files|JSON data|Comprehensions|Lambda functions|Iterators|Generators|Recursion|CLI mini-project")),
    ("Software Engineering", "Software engineering", "Learn the habits that make code understandable, testable and shareable.", _topics("Code style|Docstrings|Type hints|Virtual environments|pip and packages|Project structure|Git init and commits|Branches and merge conflicts|Unit-test basics|pytest assertions|Test fixtures|Logging|Configuration files|Refactoring|Debugging workflow")),
    ("Algorithms and Math", "Computer science and mathematics", "Use data structures, algorithms and quantitative thinking to solve problems.", _topics("Algorithm design|Big-O intuition|Arrays and linked lists|Stacks and queues|Hash tables|Trees|Graphs|Searching|Sorting|Probability basics|Statistics basics|Vectors|Matrices|Functions and graphs|Problem-solving project")),
]


TRACK_180_PHASES = {
    "agi-research": [
        ("Scientific Python", "Data and numerical computing", "Use numerical tools and data workflows used in AI research.", _topics("NumPy arrays|Array shapes|Vector operations|Matrix operations|Broadcasting|Pandas tables|Cleaning data|Data visualization|Train-test split|Feature engineering|Experiment notebook|Random seeds|Metrics|Baseline models|Data project")),
        ("Machine Learning", "Classical machine learning", "Build, evaluate and explain classical predictive models.", _topics("Linear regression|Gradient descent|Logistic regression|Classification|K-nearest neighbours|Decision trees|Ensembles|Overfitting|Regularization|Cross-validation|Accuracy|Precision and recall|F1 score|Error analysis|ML project")),
        ("Deep Learning", "Neural networks", "Understand neural networks and train small PyTorch models.", _topics("Neural-network intuition|Neurons and layers|Activation functions|Loss functions|Backpropagation|Tensors|PyTorch modules|Autograd|Training loops|Validation loops|DataLoader|Optimizers|Regularization|Model checkpoints|Digit classifier")),
        ("Language and Transformers", "NLP", "Represent text and understand the building blocks of transformer models.", _topics("Text preprocessing|Tokenization|Vocabularies|One-hot vectors|Embeddings|Sequence models|Attention intuition|Query key value|Self-attention|Positional encoding|Multi-head attention|Transformer blocks|Text classification|Tokenizer project|Mini transformer")),
        ("Reasoning and Agents", "AI reasoning", "Build simple systems that search, plan, use tools and evaluate results.", _topics("Rule-based reasoning|State and actions|Breadth-first search|Depth-first search|A-star search|Planning|Tool use|Function calling|Memory|Environments|Feedback loops|Agent evaluation|Safety boundaries|Research assistant|Agent project")),
        ("Research Practice", "Research methodology", "Design reproducible experiments and communicate their results honestly.", _topics("Research questions|Hypotheses|Baselines|Datasets|Evaluation plans|Experiment logs|Reproducibility|Ablation studies|Failure analysis|Paper reading|Result interpretation|Technical writing|Ethics and safety|Paper reproduction|Research proposal")),
        ("AI Research Capstone", "Capstone", "Integrate programming, ML and reasoning into a documented final project.", _topics("Problem selection|Requirements|Dataset plan|Baseline implementation|Experiment one|Experiment two|Evaluation|Debugging|Documentation|Demo design|Code review|Research report|Oral explanation|Final rehearsal|AI research capstone")),
    ],
    "data-science": [
        ("Data Workflow", "Data analysis", "Collect, clean and inspect structured data responsibly.", _topics("CSV datasets|Pandas DataFrames|Selecting columns|Filtering rows|Missing data|Duplicates|Data types|Grouping|Merging tables|Datetime data|Data validation|Reproducible notebooks|Data ethics|Exploratory analysis|Data cleaning project")),
        ("Statistics", "Statistics", "Use descriptive and inferential statistics to support evidence-based conclusions.", _topics("Mean median mode|Variance and standard deviation|Distributions|Sampling|Probability|Correlation|Confounding|Hypothesis tests|Confidence intervals|A/B tests|Outliers|Skewness|Statistical storytelling|Study design|Statistics project")),
        ("Visualization", "Data visualization", "Choose clear charts and communicate findings without misleading an audience.", _topics("Chart selection|Matplotlib basics|Line charts|Bar charts|Histograms|Scatter plots|Subplots|Labels and legends|Color and accessibility|Seaborn|Distribution plots|Categorical plots|Dashboard thinking|Narrative visuals|Visualization project")),
        ("Predictive Modelling", "Machine learning", "Train and compare models for real tabular-data problems.", _topics("Features and labels|Train-test split|Linear regression|Logistic regression|K-nearest neighbours|Decision trees|Random forests|Feature scaling|Pipelines|Cross-validation|Hyperparameters|Overfitting|Model comparison|Model explainability|Prediction project")),
        ("Evaluation and Deployment", "Data product practice", "Evaluate models fairly and package a useful analysis for other people.", _topics("Regression metrics|Classification metrics|Precision recall tradeoff|Data leakage|Bias checks|Error analysis|Saving models|Loading models|Simple API|Reporting results|Versioning data|Monitoring ideas|Stakeholder communication|Portfolio case study|Data product project")),
        ("Applied Data Projects", "Applied data science", "Practice the complete workflow with increasingly independent case studies.", _topics("Question framing|Dataset sourcing|Cleaning plan|Exploration|Feature plan|Baseline|Iteration|Visualization review|Model evaluation|Recommendation writing|Peer review|Reproducibility check|Portfolio writing|Presentation rehearsal|Applied project")),
        ("Data Science Capstone", "Capstone", "Deliver an end-to-end analysis and defend the conclusions.", _topics("Capstone question|Data dictionary|Analysis plan|Data preparation|Exploration report|Model baseline|Improvement experiment|Final visuals|Evaluation report|Limitations|Documentation|Demo notebook|Presentation|Final review|Data science capstone")),
    ],
    "web-dev": [
        ("Web Foundations", "Web development", "Understand how browsers, servers and HTTP work together.", _topics("How the web works|HTML structure|Semantic HTML|Forms|CSS fundamentals|Responsive layout|JavaScript overview|Browser developer tools|HTTP methods|Status codes|URLs and query strings|JSON over HTTP|Web accessibility|Web security basics|Static site project")),
        ("FastAPI APIs", "Backend development", "Build well-structured Python APIs with FastAPI.", _topics("FastAPI setup|Routes|Path parameters|Query parameters|Request bodies|Pydantic models|Responses|Validation|Error handling|Dependency injection|Async basics|OpenAPI docs|API testing|API project|API review")),
        ("Databases", "Backend development", "Persist application data with relational database design and SQL.", _topics("Relational data|Tables and keys|SQL SELECT|SQL filtering|INSERT and UPDATE|Joins|Schema design|SQLite|SQLAlchemy basics|Migrations|Transactions|Indexes|Data validation|Database project|Database review")),
        ("Full-stack Features", "Application development", "Connect user-facing pages to reliable backend features.", _topics("Frontend-backend contract|Fetch requests|Loading states|Form validation|Authentication concepts|Sessions|Authorization|Password safety|File uploads|Pagination|Search|Notifications|Error UX|Full-stack feature|Feature review")),
        ("Quality and Security", "Software engineering", "Test, secure and maintain a small web application.", _topics("Unit tests|API tests|Integration tests|Test database|Environment variables|Secrets|Input sanitization|CSRF concepts|CORS|Rate limiting|Logging|Monitoring|Accessibility audit|Security review|Quality project")),
        ("Deployment and Collaboration", "Professional practice", "Ship a web application and collaborate through a clean Git workflow.", _topics("Production configuration|Docker basics|Deployment options|CI checks|Static assets|Database backup|Error tracking|Performance basics|README writing|Issue tracking|Pull requests|Code review|Release checklist|Portfolio deployment|Launch project")),
        ("Web Development Capstone", "Capstone", "Plan, build, test and deploy a complete Python web application.", _topics("Capstone idea|User stories|Wireframes|Schema design|API plan|Frontend build|Backend build|Authentication flow|Testing pass|Security pass|Deployment|Documentation|Demo preparation|Final review|Web development capstone")),
    ],
}


# Level assessment questions per path — base set for every path.
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

# Flagship paths get path-specific extra questions.
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

# Preview lessons: full Day-1 lesson for flagship paths (kept for reference
# and future preview features; seed.py does not import this).
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

# ---------------------------------------------------------------------------
# Authored micro-curriculum for the shared topics (COMMON_180_PHASES).
# These topics appear in every launch track, so each entry upgrades three
# lessons. Keys must match COMMON_180_PHASES topic strings exactly.
# ---------------------------------------------------------------------------
COMMON_TOPIC_LIBRARY: dict[str, dict] = {
    "Boolean values": {
        "theory": "**What it is**\nEvery Python expression can be judged True or False. Comparisons produce booleans directly, and several values act falsy: 0, 0.0, '', [], {}, set(), None.\n\n**Why it matters**\nConditions, filters and while-loops all run on booleans. Misreading truthiness is a top beginner bug.\n\n**Watch out**\nbool('False') is True — any non-empty string is truthy.",
        "code": "is_enrolled = True\nscore = 0\nprint(bool(score))                  # False: zero is falsy\nprint(bool('False'))                # True: non-empty string\nprint(score or is_enrolled)         # True: or returns first truthy operand",
        "questions": ["Which values does Python treat as falsy?", "What does bool('False') return and why?", "How does `or` decide what to return?"],
        "answers": ["0, 0.0, '', [], {}, set(), None (and False itself)", "True — every non-empty string is truthy; the text content is irrelevant", "It returns the first truthy operand, or the last operand if all are falsy"],
        "homework": "Write is_study_day(weekday, is_holiday) that returns True only when weekday is between 1 and 5 AND is_holiday is False. Print the result for three different inputs.",
    },
    "Comparisons": {
        "theory": "**What it is**\nComparisons (==, !=, <, <=, >, >=) produce booleans, and Python chains them like maths: 60 <= score <= 100.\n\n**Why it matters**\nChained comparisons remove awkward `and` chains. Knowing == (value equality) versus is (identity) prevents subtle bugs.\n\n**Watch out**\nNever compare user input text with a number: '5' == 5 is False.",
        "code": "score = 72\nprint(60 <= score <= 100)      # True: chained comparison\na = [1, 2]\nb = [1, 2]\nprint(a == b, a is b)          # True False: equal value, different objects\nprint('5' == 5)                # False: text never equals a number",
        "questions": ["What does 60 <= score <= 100 mean in one sentence?", "Difference between == and is?", "Why is '5' == 5 False?"],
        "answers": ["Score is at least 60 and at most 100", "== compares values; is compares whether two names point at the same object in memory", "They are different types: a string cannot equal an integer"],
        "homework": "Write in_range(value, low, high) using a single chained comparison, and print checks for values below, inside and above the range.",
    },
    "elif decision trees": {
        "theory": "**What it is**\nif/elif/else picks exactly one branch. Python tests conditions top-down and stops at the first match.\n\n**Why it matters**\nOrdering is logic: a wrong elif order silently swallows cases. Ranges must go from specific to general.\n\n**Watch out**\nA trailing catch-all else is usually worth writing so impossible states become visible errors.",
        "code": "score = 83\nif score >= 90:\n    grade = 'A'\nelif score >= 75:\n    grade = 'B'\nelif score >= 60:\n    grade = 'C'\nelse:\n    grade = 'F'\nprint(grade)                   # B — the first matching branch wins",
        "questions": ["How many branches of an if/elif chain run?", "Why does branch order matter?", "When should you include a final else?"],
        "answers": ["Exactly one — the first condition that is true", "Because evaluation stops at the first true condition; broad conditions first hide later ones", "Almost always: it makes unexpected data explicit instead of silently ignored"],
        "homework": "Write classify_streak(days) printing 'cold' (<3), 'warming' (3-6), 'on fire' (7+) using an elif chain, and prove all four paths print something different.",
    },
    "Nested conditions": {
        "theory": "**What it is**\nAn if inside another if expresses combined requirements: outer gate, inner detail.\n\n**Why it matters**\nReal rules are layered (enrolled AND attended AND submitted). Nesting models that directly — but deep nesting hurts readability.\n\n**Watch out**\nMore than two levels deep usually means you should combine conditions or extract a function.",
        "code": "enrolled = True\nattendance = 80\nif enrolled:\n    if attendance >= 75:\n        print('Exam allowed')\n    else:\n        print('Attendance too low')\nelse:\n    print('Not enrolled')",
        "questions": ["What rule do nested ifs express here?", "When does nesting become harmful?", "Name one alternative to deep nesting."],
        "answers": ["Exam requires enrollment first, and separately at least 75% attendance", "Past about two levels: indentation grows and the happy path becomes hard to see", "Combine with and/or into one condition, or extract a well-named helper function"],
        "homework": "Write can_graduate(xp, penalties, project_done) with nested checks: xp >= 500 and penalties == 0 and project_done. Print one clear reason string for every failure path.",
    },
    "while loops": {
        "theory": "**What it is**\nwhile repeats as long as its condition stays True — unlike for, it can run an unknown number of times.\n\n**Why it matters**\nCountdowns, input retry loops and 'until the user quits' patterns need while.\n\n**Watch out**\nIf nothing inside the loop moves the condition toward False you get an infinite loop. Always change the loop variable.",
        "code": "energy = 3\nwhile energy > 0:\n    print('Study session left:', energy)\n    energy -= 1          # without this line the loop never ends\nprint('Done for today')",
        "questions": ["When is while better than for?", "What causes an infinite while loop?", "Where must the state change happen?"],
        "answers": ["When the number of repetitions is not known in advance — it depends on a condition", "The condition never becomes False because nothing updates the variables it depends on", "Inside the loop body, on a path that always executes (or via break)"],
        "homework": "Simulate saving money: start at balance 0, add 25 per week while balance < 200, and print the week number when the target is reached.",
    },
    "Loop control": {
        "theory": "**What it is**\nbreak exits the loop immediately, continue jumps to the next iteration, pass does nothing (placeholder).\n\n**Why it matters**\nThey express 'stop at first match' and 'skip invalid rows' cleanly without flag variables.\n\n**Watch out**\ncontinue placed before the counter update in a while-loop causes an infinite loop.",
        "code": "for day in range(1, 8):\n    if day in (6, 7):\n        continue          # skip weekends\n    if day == 5:\n        break             # stop early at day 5\n    print('Studied day', day)",
        "questions": ["Difference between break and continue?", "Why is pass useful?", "Which loop-control bug involves while + continue?"],
        "answers": ["break terminates the whole loop; continue skips only the rest of the current iteration", "It is a syntactic placeholder where Python demands a statement but you have no logic yet", "Putting continue before the variable update, skipping the update forever"],
        "homework": "Loop over numbers 1-20: skip multiples of 3 with continue, stop at the first multiple of 9 with break, and print every number you processed.",
    },
    "String indexing": {
        "theory": "**What it is**\nStrings are sequences: word[0] is the first character, word[-1] the last, word[1:4] a slice.\n\n**Why it matters**\nParsing filenames, codes and user input all start with indexing and slicing.\n\n**Watch out**\nIndexing out of range raises IndexError, but slices silently clip instead of failing.",
        "code": "word = 'PySchool'\nprint(word[0], word[-1])     # P l\nprint(word[2:5])             # Sch\nprint(word[::-1])            # loohcSyP — step -1 reverses\nprint(word[50:])             # '' — slices clip, no error",
        "questions": ["What does word[-1] give?", "Difference between indexing and slicing on bad positions?", "How do you reverse a string with a slice?"],
        "answers": ["The last character", "Bad index raises IndexError; a bad slice just clips to the valid range and returns what exists", "word[::-1] — full slice with step -1"],
        "homework": "Write initials(fullname) that builds initials from the first letters of each word using indexing, and print initials for two names.",
    },
    "String methods": {
        "theory": "**What it is**\nStrings ship with methods: .lower(), .strip(), .split(), .replace(), .startswith(). They return NEW strings.\n\n**Why it matters**\nNormalising input (trim + lowercase) is the first line of defence in comparing and storing text.\n\n**Watch out**\nStrings are immutable — text.strip() does nothing unless you assign the result.",
        "code": "raw = '  Hello PySchool  '\nclean = raw.strip().lower()\nprint(repr(clean))               # 'hello pyschool'\nprint(raw)                       # unchanged! strings are immutable\nprint('a,b,c'.split(','))        # ['a', 'b', 'c']",
        "questions": ["What does .strip() remove?", "Why doesn't raw change after calling methods on it?", "What does .split(',') return?"],
        "answers": ["Leading and trailing whitespace (spaces, tabs, newlines)", "Strings are immutable — methods return new strings, so you must capture the result", "A list of substrings split at each comma"],
        "homework": "Write normalise(email) returning email.strip().lower(), then check it against ' A@X.com ', proving the stored value differs from the input.",
    },
}

COMMON_TOPIC_LIBRARY.update({
    "List methods": {
        "theory": "**What it is**\nLists mutate in place: .append(), .insert(), .remove(), .sort(), .pop().\n\n**Why it matters**\nLists are the everyday workhorse container; in-place mutation is convenient but surprising.\n\n**Watch out**\nsort(), append() and reverse() return None — writing lst = lst.sort() destroys your list reference.",
        "code": "topics = ['loops', 'strings']\ntopics.append('dicts')\ntopics.sort()\nremoved = topics.pop(0)\nprint(topics, '| removed:', removed)\nprint(topics.sort())             # None! sort works in place",
        "questions": ["What does topics.sort() return?", "How do you delete by value vs by position?", "Difference between append and insert?"],
        "answers": ["None — it sorts the list in place, so never assign its result", ".remove(value) deletes the first matching value; .pop(index) deletes and returns the item at a position", "append adds at the end; insert(i, x) adds at position i and shifts the rest right"],
        "homework": "Build a study queue: append three topics, insert 'revision' at position 0, pop the first item, then print the final queue sorted alphabetically.",
    },
    "Tuples and unpacking": {
        "theory": "**What it is**\nTuples are fixed-size, immutable sequences written (a, b). Unpacking assigns elements to names in one line: x, y = point.\n\n**Why it matters**\nFunctions naturally return tuples; unpacking makes multi-value results readable.\n\n**Watch out**\nOne-element tuples need a comma: (42,) is a tuple, (42) is just the int 42.",
        "code": "point = (3, 7)\nx, y = point                 # unpacking\nprint(x + y)                 # 10\ndef min_max(nums):\n    return min(nums), max(nums)\nlow, high = min_max([4, 9, 1])\nprint(low, high)             # 1 9",
        "questions": ["How is a tuple different from a list?", "What does 'return min(nums), max(nums)' actually return?", "How do you write a one-element tuple?"],
        "answers": ["Tuples are immutable and fixed-length; lists are mutable", "A tuple (min_value, max_value)", "(42,) — the trailing comma makes the tuple"],
        "homework": "Write stats(nums) returning (total, average) as a tuple, unpack both into names, and print a summary line using them.",
    },
    "Sets": {
        "theory": "**What it is**\nA set stores unique, unordered items: {1, 2, 3}. Membership tests (x in s) are very fast, and duplicates collapse automatically.\n\n**Why it matters**\nDeduplicating lists and fast 'have I seen this?' checks are daily tasks.\n\n**Watch out**\nSets have no order — don't rely on index positions; an empty set is set(), not {} (that's a dict).",
        "code": "visits = ['maths', 'english', 'maths', 'code']\nunique = set(visits)\nprint(unique)                    # order not guaranteed\nprint('maths' in unique)         # fast membership\nprint(len(visits), len(unique))  # 4 3",
        "questions": ["What happens to duplicates in a set?", "Why is membership testing in sets fast?", "How do you create an empty set?"],
        "answers": ["They disappear — each value appears at most once", "Sets are hash-based like dictionaries, giving roughly constant-time lookups", "set() — curly braces alone create an empty dictionary"],
        "homework": "Write unique_topics(topic_list) that returns how many distinct topics were studied, and demonstrate it on a list containing at least one repeat.",
    },
    "Dictionary methods": {
        "theory": "**What it is**\nDicts map keys to values. Key methods: .get(key, default) reads safely, .items() loops pairs, del removes.\n\n**Why it matters**\n.get() replaces clumsy 'check then read' code and avoids KeyError.\n\n**Watch out**\nReading a missing key with [] raises KeyError; .get() returns None (or your default) instead.",
        "code": "scores = {'python': 85}\nprint(scores.get('maths'))            # None — no crash\nprint(scores.get('maths', 0))         # 0 — explicit default\nscores['maths'] = 91\nfor subject, mark in scores.items():\n    print(subject, mark)",
        "questions": ["Difference between d[k] and d.get(k)?", "What does .items() yield in a loop?", "How do you add or overwrite a key?"],
        "answers": ["d[k] raises KeyError when missing; d.get(k) returns None or a supplied default", "Key-value tuples, one per iteration: for key, value in d.items()", "Assignment: d[new_key] = value creates or overwrites"],
        "homework": "Store three subject marks in a dict, then print each with .items() and safely print a missing subject using .get with default 'no exam yet'.",
    },
    "Function parameters": {
        "theory": "**What it is**\nParameters receive arguments positionally or by keyword; defaults make them optional: def greet(name, greeting='Hi').\n\n**Why it matters**\nGood parameter design (defaults, keywords) keeps calls readable as functions grow.\n\n**Watch out**\nNever use a mutable default like def add(item, bag=[]): the list is shared across ALL calls.",
        "code": "def greet(name, greeting='Hi'):\n    return f'{greeting}, {name}!'\n\nprint(greet('Riya'))                    # positional + default\nprint(greet(name='Aarav', greeting='Welcome'))  # keywords\n\ndef bad(bucket=[]):                     # DON'T do this\n    bucket.append(1)\n    return bucket\nprint(bad(), bad())                     # [1] [1, 1] — shared!",
        "questions": ["What is a keyword argument?", "Why are mutable defaults dangerous?", "How do defaults make APIs friendlier?"],
        "answers": ["An argument passed as name=value, letting you reorder or skip optional parameters", "The default object is created once and shared between calls, so mutations leak between callers", "Callers specify only what differs from the common case"],
        "homework": "Write estimate(hours, rate=150, bonus=0) returning total pay, call it three ways (positional, keyword, mixed) and print each result.",
    },
    "Return values": {
        "theory": "**What it is**\nreturn sends a result back to the caller and ends the function immediately. No return means the function returns None.\n\n**Why it matters**\nReturning (instead of only printing) lets results compose into bigger programs and tests.\n\n**Watch out**\nCode after an executed return never runs — handy for early exits, deadly by accident.",
        "code": "def pass_or_fail(score):\n    if score >= 60:\n        return 'pass'          # early exit\n    return 'fail'\n\nresult = pass_or_fail(45)\nprint(result.upper())\ndef nothing():\n    x = 1\nprint(nothing())               # None",
        "questions": ["What does a function without return give back?", "Two benefits of returning instead of printing", "What is an early return?"],
        "answers": ["None", "Results can be stored, transformed and reused; automated tests can assert on them", "Returning from the middle of a function as soon as the answer is known, skipping remaining code"],
        "homework": "Rewrite a print-only function you wrote earlier so it RETURNS its result, store it in a variable, and print a sentence built from that variable.",
    },
    "Variable scope": {
        "theory": "**What it is**\nNames created inside a function are local — they vanish when the function ends. Functions read outer names fine, but assigning needs care.\n\n**Why it matters**\nScope explains 'UnboundLocalError' and why functions shouldn't silently depend on faraway globals.\n\n**Watch out**\nglobal is almost always the wrong fix; pass data in as parameters and out as returns.",
        "code": "streak = 4                    # global\n\ndef next_streak(current):     # data flows IN via parameter\n    doubled = current * 2     # local name\n    return doubled            # data flows OUT via return\n\nprint(next_streak(streak))\nprint(streak)                 # unchanged",
        "questions": ["Where can a local variable be used?", "What happens if you assign to a global name inside a function without declaring global?", "Better alternative to global?"],
        "answers": ["Only inside the function that created it, and only while that call is running", "Python treats the name as local, so reading it before assignment raises UnboundLocalError", "Take the value as a parameter and return the new value"],
        "homework": "Demonstrate scope: write a function with a local variable that shadows a global of the same name, print both, and explain the output in comments.",
    },
})

# --- Practical Python (shared phase 2) --------------------------------------
COMMON_TOPIC_LIBRARY.update({
    "Modules and imports": {
        "theory": "**What it is**\nModules are files of reusable code. `import math` brings the whole module; `from math import sqrt` brings one name.\n\n**Why it matters**\nImports unlock the standard library and every installed package — you never code alone.\n\n**Watch out**\nNever name your file after a module you import (a personal `random.py` shadows the real one).",
        "code": "import math\nfrom datetime import date\n\nprint(math.sqrt(144))          # 12.0\nprint(date.today().year)\nprint(math.ceil(7.2))",
        "questions": ["Difference between import math and from math import sqrt?", "What is the module shadowing trap?", "How do you get today's date via imports?"],
        "answers": ["The first keeps names namespaced (math.sqrt); the second binds sqrt directly into your namespace", "A local file with the same name as a standard module hides the original from imports", "from datetime import date, then call date.today()"],
        "homework": "Import two stdlib modules, use one function from each (e.g. math.floor and random.randint), and print both results with explanatory comments.",
    },
    "Standard library tour": {
        "theory": "**What it is**\nPython ships 'batteries included': math, random, datetime, pathlib, json, csv, collections and more — no installation needed.\n\n**Why it matters**\nBefore writing a helper, check the stdlib: it is tested, documented and faster than hand-rolling.\n\n**Watch out**\nDon't memorise it — learn to browse docs and use help() instead.",
        "code": "import random\nfrom collections import Counter\n\nrolls = [random.randint(1, 6) for _ in range(50)]\nprint(Counter(rolls).most_common(2))   # two most frequent faces",
        "questions": ["Name three stdlib modules useful for data work", "Why prefer stdlib over writing your own utility?", "What does Counter do?"],
        "answers": ["json, csv, collections (also statistics, pathlib)", "It is already tested, documented and maintained — spend your time on your problem instead", "Counts occurrences of each item and can rank them with most_common()"],
        "homework": "Use random + Counter to simulate 100 coin tosses and print the head/tally counts; comment which module did what.",
    },
    "Command-line arguments": {
        "theory": "**What it is**\nsys.argv holds the words typed after your script name: argv[0] is the script, argv[1:] are user arguments.\n\n**Why it matters**\nArguments make scripts reusable without editing code — same script, different inputs.\n\n**Watch out**\nargv items are always strings; convert to int yourself and handle missing arguments.",
        "code": "import sys\n\nargs = sys.argv[1:]\nif len(args) < 1:\n    print('Usage: python script.py <name>')\nelse:\n    print(f'Hello, {args[0]}!')",
        "questions": ["What is stored in sys.argv[0]?", "Are command-line arguments strings or numbers?", "Why guard len(args) before indexing?"],
        "answers": ["The path/name of the running script itself", "Always strings — convert with int() or float() when maths is needed", "Indexing an empty argv list raises IndexError"],
        "homework": "Write greeting logic that accepts a name argument and prints a greeting, printing a usage message when no argument is given.",
    },
    "Input validation": {
        "theory": "**What it is**\nValidation checks data BEFORE using it: type, range, format. Reject early with clear messages.\n\n**Why it matters**\nGarbage in, crash later. A validated int in range 1-100 prevents ten downstream bugs.\n\n**Watch out**\nint('3.5') raises ValueError — validate with try/except, not by hoping.",
        "code": "def read_score(raw):\n    try:\n        value = int(raw)\n    except ValueError:\n        return None, 'not a whole number'\n    if not 0 <= value <= 100:\n        return None, 'outside 0-100'\n    return value, 'ok'\n\nprint(read_score('82'))\nprint(read_score('abc'))\nprint(read_score('150'))",
        "questions": ["Why validate at the boundary?", "Which exception does int('abc') raise?", "What makes a good validation error message?"],
        "answers": ["Bad data is cheapest to reject at entry, before it spreads through the program", "ValueError", "Says what was wrong AND what is acceptable, e.g. 'score must be 0-100'"],
        "homework": "Write validate_age(text) returning (value, message): reject non-integers and ages outside 5-100, print results for three test inputs.",
    },
    "Exceptions": {
        "theory": "**What it is**\ntry/except catches runtime errors so one bad value doesn't kill the program. else runs on success; finally always runs.\n\n**Why it matters**\nFiles miss, users mistype, networks drop — robust programs expect failure and recover.\n\n**Watch out**\nCatch SPECIFIC exceptions (ValueError, KeyError). Bare except hides real bugs including typos.",
        "code": "try:\n    hours = int('ten')\nexcept ValueError as error:\n    print('Bad number:', error)\nelse:\n    print('Parsed:', hours)\nfinally:\n    print('Validation attempt finished')",
        "questions": ["When does the else block run?", "Why avoid a bare except?", "What is finally for?"],
        "answers": ["Only when no exception was raised in the try block", "It swallows every error type, masking genuine bugs like NameError from typos", "Cleanup code that must run whether or not an exception occurred"],
        "homework": "Wrap a risky int conversion in try/except/else/finally, feeding it one good and one bad input, and print a different line in each block.",
    },
    "Custom exceptions": {
        "theory": "**What it is**\nYou can define your own errors by subclassing Exception: class LowAttendance(Exception).\n\n**Why it matters**\nDomain-specific names document rules and let callers catch YOUR failures precisely.\n\n**Watch out**\nRaise with a helpful message; keep hierarchy shallow.",
        "code": "class InsufficientXp(Exception):\n    pass\n\ndef unlock_module(xp, cost):\n    if xp < cost:\n        raise InsufficientXp(f'need {cost}, have {xp}')\n    return 'unlocked'\n\ntry:\n    print(unlock_module(40, 100))\nexcept InsufficientXp as error:\n    print('Locked:', error)",
        "questions": ["How do you create a custom exception?", "Why give custom exceptions descriptive names?", "Who raises vs who catches?"],
        "answers": ["Subclass Exception and raise it where the rule breaks", "The name becomes part of the API and the error log — it should state the broken rule", "The function detecting the broken rule raises; the caller decides how to recover"],
        "homework": "Define EmptySubmission(Exception), write submit(code) that raises it for blank code, and catch it printing an encouraging retry message.",
    },
    "Reading text files": {
        "theory": "**What it is**\n`with open(path) as f:` opens a file and guarantees closing. Modes: 'r' read, 'w' overwrite, 'a' append.\n\n**Why it matters**\nLogs, configs, datasets — most real data enters programs through files.\n\n**Watch out**\n'w' erases immediately on open. Iterate lines and .strip() newline characters.",
        "code": "with open('log.txt', 'w') as f:\n    f.write('day 1: ok\\n')\n    f.write('day 2: ok\\n')\n\nwith open('log.txt') as f:\n    for line_number, line in enumerate(f, start=1):\n        print(line_number, line.strip())",
        "questions": ["Why use with instead of open/close?", "Difference between 'w' and 'a'?", "Why strip() each line?"],
        "answers": ["with closes the file even if an exception happens mid-block", "'w' truncates (erases) the file at open; 'a' appends to whatever exists", "Each line still carries its trailing newline character"],
        "homework": "Write three study-log lines to notes.txt, then read the file back and print only lines containing 'python'.",
    },
})

COMMON_TOPIC_LIBRARY.update({
    "Writing CSV files": {
        "theory": "**What it is**\ncsv writes rows of values as comma-separated lines that Excel/pandas open natively.\n\n**Why it matters**\nCSV is the universal small-data exchange format between your code and spreadsheets.\n\n**Watch out**\nUse csv.writer rather than gluing commas yourself — it handles quoting when values contain commas.",
        "code": "import csv, io\n\nbuffer = io.StringIO()               # pretend-file so the example is printable\nwriter = csv.writer(buffer)\nwriter.writerow(['subject', 'mark'])\nwriter.writerow(['python', 85])\nprint(buffer.getvalue())",
        "questions": ["Why not just join values with ',' manually?", "What does writerow take?", "Why write into io.StringIO here?"],
        "answers": ["The csv module quotes fields containing commas/quotes correctly — manual joining corrupts rows", "An iterable (list/tuple) representing one row", "So the demo prints its output anywhere without touching your disk"],
        "homework": "Build rows for three students (name, score), serialise them with csv.writer into io.StringIO, and print the CSV text.",
    },
    "JSON data": {
        "theory": "**What it is**\njson.dumps(obj) turns Python dicts/lists into JSON text; json.loads(text) parses back. It's the language of web APIs.\n\n**Why it matters**\nAPIs, config files and document stores all speak JSON — round-tripping is a core skill.\n\n**Watch out**\nJSON keys are always strings; tuples come back as lists, and set() cannot be dumped at all.",
        "code": "import json\n\nstudent = {'name': 'Riya', 'xp': 120, 'topics': ['loops', 'sets']}\ntext = json.dumps(student, indent=2)\nprint(text)\nback = json.loads(text)\nprint(back['xp'] + 10)",
        "questions": ["Which Python types survive a JSON round-trip?", "What does indent=2 change?", "Why can't a set be dumped?"],
        "answers": ["dict (str keys), list, str, int, float, bool, None — tuples arrive back as lists", "Pretty-prints with two-space indentation for humans", "JSON has no set concept — convert to list first"],
        "homework": "Create a profile dict (name, level, skills list), dumps it with indent, loads it back, and print one field from the recovered object.",
    },
    "Comprehensions": {
        "theory": "**What it is**\nComprehensions build lists in one readable line: [x*x for x in nums if x % 2 == 0]. Dict/set comprehensions exist too.\n\n**Why it matters**\nThey replace 4-line loops with intent-revealing one-liners — the Pythonic idiom for transforms.\n\n**Watch out**\nIf the expression needs nested ifs and a second loop, go back to a normal loop: readability wins.",
        "code": "scores = [45, 82, 91, 58]\npassing = [s for s in scores if s >= 60]\nlabels = {s: ('pass' if s >= 60 else 'fail') for s in scores}\nprint(passing)     # [82, 91]\nprint(labels)",
        "questions": ["Translate [x*2 for x in nums] into a for-loop", "Where does the filter condition go?", "When should you NOT use a comprehension?"],
        "answers": ["result = []; then for x in nums: result.append(x * 2)", "After the loop part: [x for x in nums if condition]", "When logic needs multiple steps or nesting gets deep — a plain loop reads better"],
        "homework": "Given a marks list, build (in one comprehension each) the passing list and a pass/fail label dict, and print both.",
    },
    "Lambda functions": {
        "theory": "**What it is**\nA lambda is a tiny unnamed expression-function: lambda x: x * 2. Main use: short sort/filter keys.\n\n**Why it matters**\nsorted(data, key=lambda row: row[1]) expresses 'order by second column' inline.\n\n**Watch out**\nLambdas can't contain statements. If it doesn't fit one expression, write def.",
        "code": "students = [('Riya', 85), ('Aarav', 92), ('Kabir', 78)]\nby_mark = sorted(students, key=lambda pair: pair[1], reverse=True)\nprint(by_mark)",
        "questions": ["What can a lambda body contain?", "Most idiomatic lambda use case?", "When must you switch to def?"],
        "answers": ["A single expression — statements like loops, assignments or return are not allowed", "As the key= argument to sorted(), min(), max()", "As soon as you need multiple steps, comments, or reuse under a name"],
        "homework": "Sort a list of (topic, hours) tuples by hours descending using sorted + lambda, and print the ranked study plan.",
    },
    "Iterators": {
        "theory": "**What it is**\nAn iterator yields values one at a time via next(); raising StopIteration when finished. iter(list) produces one.\n\n**Why it matters**\nfor-loops are iterators underneath. Understanding them explains lazy behaviour of files, generators and streams.\n\n**Watch out**\nIterators exhaust: a second pass over the same iterator yields nothing.",
        "code": "days = iter(['mon', 'tue', 'wed'])\nprint(next(days))\nprint(next(days))\nrest = list(days)             # collect what's left\nprint(rest)\nprint(next(days, 'exhausted')) # default avoids StopIteration",
        "questions": ["What does next() return at the end?", "How is a for-loop related to iterators?", "What happens when you iterate an exhausted iterator?"],
        "answers": ["It raises StopIteration (or returns the supplied default)", "for calls iter() then repeatedly next(), stopping silently at StopIteration", "Nothing — zero iterations; the iterator stays empty"],
        "homework": "Manually step through iter([10, 20, 30]) with next() twice, convert the remainder with list(), and print all three stages.",
    },
    "Generators": {
        "theory": "**What it is**\nA generator function uses yield to emit values lazily, pausing between requests.\n\n**Why it matters**\nGenerate infinite or huge sequences with constant memory — values are computed only when asked.\n\n**Watch out**\nLike iterators they're single-use; call the generator function again for a fresh stream.",
        "code": "def study_streak(limit):\n    day = 1\n    while day <= limit:\n        yield f'day {day}'\n        day += 1\n\nplan = study_streak(3)\nprint(next(plan))\nprint(list(plan))            # remaining items",
        "questions": ["What does yield do that return doesn't?", "Why are generators memory-friendly?", "How many times can you consume one generator object?"],
        "answers": ["yield pauses and preserves local state, resuming on the next request; return ends permanently", "Values are produced one at a time on demand — never the whole sequence in memory", "Exactly once; afterwards it is empty"],
        "homework": "Write a generator countdown(n) yielding n down to 1, consume the first value with next(), then print the rest with a loop.",
    },
    "Recursion": {
        "theory": "**What it is**\nA recursive function calls itself on a smaller input until a BASE CASE stops the descent.\n\n**Why it matters**\nTrees, folders and nested JSON are naturally recursive structures — recursion mirrors their shape.\n\n**Watch out**\nMissing/wrong base case means RecursionError. Every call consumes stack space.",
        "code": "def factorial(n):\n    if n <= 1:              # base case — mandatory!\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))         # 120\nprint(factorial(0))         # 1 — base case handles it",
        "questions": ["What two parts does every recursion need?", "What happens without a working base case?", "Name a structure best traversed recursively"],
        "answers": ["A base case that returns directly, and a recursive step moving toward that base case", "It calls itself forever until Python raises RecursionError", "Nested trees: folder hierarchies, JSON documents"],
        "homework": "Write recursive total_study(days) summing 1+2+...+n minutes, print results for n=5 and n=0, and comment which line is the base case.",
    },
    "CLI mini-project": {
        "theory": "**What it is**\nCombining arguments, validation and functions into a small command-line tool.\n\n**Why it matters**\nThis is your first SHIPPED artifact: others run it without reading your code.\n\n**Watch out**\nKeep main() thin: parse → validate → act → report.",
        "code": "def report(name, days):\n    badge = 'on fire' if days >= 7 else 'building'\n    return f'{name}: {days}-day streak ({badge})'\n\ndef parse(args):\n    if len(args) != 2:\n        raise SystemExit('usage: streak.py <name> <days>')\n    return args[0], int(args[1])\n\nname, days = parse(['riya', '9'])   # simulate sys.argv[1:]\nprint(report(name, days))",
        "questions": ["What four stages does a clean CLI tool separate?", "Why keep logic out of main()?", "What does SystemExit('msg') do?"],
        "answers": ["Parse arguments, validate them, perform the action, report the result", "Thin main keeps each piece testable and importable by other code", "Prints the message and exits with non-zero status"],
        "homework": "Extend the example: support a 'shout' mode argument that upper-cases the report, and demonstrate both modes in printed output.",
    },
})

# --- Software Engineering (shared phase 3) ----------------------------------
COMMON_TOPIC_LIBRARY.update({
    "Code style": {
        "theory": "**What it is**\nPEP 8 conventions: snake_case names, 4-space indents, spaces around operators.\n\n**Why it matters**\nConsistent style lets any Python developer read your code at full speed — including future you.\n\n**Watch out**\nInconsistent naming hides logic differences (total vs Total).",
        "code": "# Before (works, but fights the reader)\ndef Calc(x,y):\n    return x+y\n\n# After (PEP 8)\ndef calculate_total(price, quantity):\n    return price + quantity\n\nprint(calculate_total(3, 4))",
        "questions": ["How are variables and functions named in PEP 8?", "Two style rules besides naming?", "Why does consistent style matter in teams?"],
        "answers": ["snake_case — lowercase words separated by underscores", "4-space indentation; spaces around operators; short lines", "Everyone reads everyone's code; a shared style removes translation cost"],
        "homework": "Take the 'Before' function, rename it and its parameters per PEP 8 with operator spacing, then print both versions' results to prove identical behaviour.",
    },
    "Docstrings": {
        "theory": "**What it is**\nA docstring is a triple-quoted description on the first line of a function/class/module. help(obj) reads it back.\n\n**Why it matters**\nDocstrings are documentation that lives WITH the code and shows up in editors.\n\n**Watch out**\nSay WHAT and WHY plus parameter meaning — not a restatement of the name.",
        "code": "def study_total(hours_per_day, days):\n    \"\"\"Return total study hours over a period.\n\n    Args:\n        hours_per_day: daily commitment in hours.\n        days: number of days (> 0).\n    \"\"\"\n    return hours_per_day * days\n\nprint(study_total(1.5, 20))\nprint(study_total.__doc__.splitlines()[0])",
        "questions": ["Where must a docstring be placed?", "What does help(study_total) display?", "What makes a bad docstring?"],
        "answers": ["Immediately after the def/class/module line, in triple quotes", "The docstring text, nicely formatted", "Repeating the function name without explaining parameters or purpose"],
        "homework": "Write a function with a full docstring (args + returns), call it once, and print its first docstring line via __doc__.",
    },
    "Type hints": {
        "theory": "**What it is**\nAnnotations like def pay(hours: float, rate: float = 150) -> float document expected types. Python does not enforce them at runtime by default.\n\n**Why it matters**\nHints turn runtime surprises into editor warnings; tools can check them statically.\n\n**Watch out**\nHints don't validate input — conversion is still your job.",
        "code": "def payout(hours: float, rate: float = 150) -> float:\n    return hours * rate\n\ndef banner(name: str) -> str:\n    return f'== {name} =='\n\nprint(payout(2.5))\nprint(banner('PySchool'))",
        "questions": ["Do type hints change how Python runs your code?", "What does the -> float part mean?", "Name one tool that checks hints"],
        "answers": ["No — they're metadata for readers and tools, ignored by the interpreter", "The function's declared return type", "mypy (also pyright / IDE checkers)"],
        "homework": "Annotate a two-parameter function fully (params + return), deliberately pass a wrong-typed value, print the result anyway and comment what did or did not happen.",
    },
    "Virtual environments": {
        "theory": "**What it is**\nA venv is a private per-project Python install. Create: python -m venv .venv; activate: source .venv/bin/activate.\n\n**Why it matters**\nProject A needs pandas 1.x, project B needs 2.x — venvs isolate dependencies.\n\n**Watch out**\nThe venv folder is machine-specific: never commit it; commit requirements.txt instead.",
        "code": "# Terminal commands (not Python):\n# python -m venv .venv          # create\n# source .venv/bin/activate     # activate (Linux/macOS)\n# deactivate                    # leave\n\nimport sys\nprint(sys.prefix)   # inside an activated venv this shows the .venv path",
        "questions": ["What problem do virtual environments solve?", "Which commands create and activate one?", "Should .venv be committed to git?"],
        "answers": ["Dependency isolation: different projects can use different package versions safely", "python -m venv .venv, then source .venv/bin/activate (Linux/macOS)", "No — reproduce it from requirements.txt instead"],
        "homework": "Print sys.executable and sys.prefix, and write comments listing the exact commands to create and activate a venv named .venv.",
    },
    "pip and packages": {
        "theory": "**What it is**\npip installs third-party packages: pip install requests. pip freeze > requirements.txt pins versions.\n\n**Why it matters**\nThe PyPI ecosystem is Python's superpower — but only reproducible when pinned.\n\n**Watch out**\nInstall into the ACTIVATED venv, otherwise packages land in the wrong interpreter.",
        "code": "# Terminal commands:\n# pip install rich            # add a package\n# pip freeze > requirements.txt   # pin exact versions\n# pip install -r requirements.txt # recreate elsewhere\n\nimport importlib.metadata as md\ntry:\n    print('rich version:', md.version('rich'))\nexcept md.PackageNotFoundError:\n    print('not installed here — that is fine too')",
        "questions": ["What does pip freeze capture?", "Why pin versions in requirements.txt?", "Where should pip install run?"],
        "answers": ["Exact installed versions of all packages in the current environment", "So tomorrow's install gets tested versions instead of whatever is newest", "Inside the activated project venv"],
        "homework": "Print whether two packages are installed using importlib.metadata, with comments showing the pip commands to add them.",
    },
    "Project structure": {
        "theory": "**What it is**\nA predictable layout separates code, tests and docs: app/ package, tests/, README.md, requirements.txt.\n\n**Why it matters**\nStandard structure means tools (pytest, pip) and humans find everything without asking.\n\n**Watch out**\nDon't keep everything in one script forever — extract a package once modules import each other.",
        "code": "# pyschool/\n# ├── backend/app/main.py     # entrypoint\n# ├── backend/app/routers/    # endpoint modules\n# ├── frontend/src/pages/     # UI pages\n# ├── tests/\n# └── README.md\nfrom pathlib import Path\nfor item in sorted(Path('.').iterdir()):\n    print(item.name)",
        "questions": ["Name four standard entries in a small project layout", "Why does pytest care about structure?", "When should scripts become a package?"],
        "answers": ["Package dir, tests/, README.md, requirements.txt", "It auto-discovers test_*.py files under known directories", "Once there are multiple modules importing each other"],
        "homework": "List your current directory contents with pathlib and comment where tests/, docs and config would live in the standard layout.",
    },
    "Git init and commits": {
        "theory": "**What it is**\ngit init creates a repository; each commit is a labelled snapshot whose message describes WHY the change exists.\n\n**Why it matters**\nCommits are undo points and a changelog: small, frequent, well-messaged commits save hours.\n\n**Watch out**\n'fix stuff' messages waste their purpose. Write imperative summaries.",
        "code": "# Terminal workflow:\n# git init                       # start tracking\n# git status                     # what changed?\n# git add app/routers/lessons.py # stage chosen files\n# git commit -m 'Fix rubric whitespace matching'\n# git log --oneline              # history",
        "questions": ["What does a commit snapshot contain?", "Difference between git add and git commit?", "What makes a good commit message?"],
        "answers": ["The staged state of tracked files plus parent link, author, timestamp and message", "add stages selected changes; commit records ALL staged changes permanently", "A short imperative summary of why the change was made"],
        "homework": "Write comments simulating your next three commits (file + message each) and print a fake git-log output built from strings.",
    },
})

COMMON_TOPIC_LIBRARY.update({
    "Branches and merge conflicts": {
        "theory": "**What it is**\nA branch is a parallel line of work: git switch -c feature-x. When two branches edit the same lines, merging raises a conflict marked with <<<, ===, >>>.\n\n**Why it matters**\nBranches let you experiment safely; conflict resolution is everyday teamwork.\n\n**Watch out**\nConflicts aren't errors — they're questions about which version survives.",
        "code": "# git switch -c feature-streak     # new branch\n# git switch main && git merge feature-streak\n#\n# A conflict looks like:\n# <<<<<<< main\n# streak = 7\n# =======\n# streak = 10\n# >>>>>>> feature-streak\nstreak = 10   # resolved: keep one side, delete markers",
        "questions": ["Which command creates and switches to a new branch?", "When do merge conflicts appear?", "How do you resolve a conflicted hunk?"],
        "answers": ["git switch -c <name>", "When both branches changed the same lines and neither has been merged yet", "Edit the file to keep the intended content and remove the marker lines"],
        "homework": "Simulate a conflict: define the same variable twice with conflict-marker comments, then write the resolved line and explain your choice in a comment.",
    },
    "Unit-test basics": {
        "theory": "**What it is**\nA unit test calls one function with known inputs and asserts the expected output.\n\n**Why it matters**\nTests let you change code bravely: break behaviour and they scream immediately.\n\n**Watch out**\nTest behaviour (returned values), not implementation details.",
        "code": "def apply_penalty(xp, amount=5):\n    return max(0, xp - amount)\n\ndef test_penalty_reduces_xp():\n    assert apply_penalty(50) == 45\n\ndef test_penalty_never_negative():\n    assert apply_penalty(3, 10) == 0\n\ntest_penalty_reduces_xp()\ntest_penalty_never_negative()\nprint('both tests passed')",
        "questions": ["What three parts make up one unit test?", "Why run tests after refactoring?", "What should you assert on?"],
        "answers": ["Arrange inputs, act (call the function), assert the expected result", "Refactoring changes internals; tests prove external behaviour survived", "Observable outputs — return values and raised exceptions"],
        "homework": "Write two tests for an is_pass(score) helper (boundary 60 included), run them, and print a success confirmation only if every assertion holds.",
    },
    "pytest assertions": {
        "theory": "**What it is**\npytest runs functions named test_* and uses plain assert with optional messages.\n\n**Why it matters**\nNo boilerplate; failure output shows exactly which expression broke.\n\n**Watch out**\nA test with no assertion always passes — testing nothing is worse than not testing.",
        "code": "# saved as test_rubric.py, run with: pytest -q\ndef pattern_found(pattern, code):\n    return pattern.replace(' ', '') in code.replace(' ', '')\n\ndef test_tolerates_space_before_paren():\n    assert pattern_found('print(', \"print ('hi')\")\n\ndef test_rejects_wrong_name():\n    assert not pattern_found('print(', 'myprint(\"hi\")')",
        "questions": ["How does pytest discover tests?", "Why add a message to an assert?", "What is the danger of an assertion-free test?"],
        "answers": ["Files matching test_*.py, collecting functions named test_*", "On failure the message explains intent, speeding diagnosis", "It cannot fail, giving false confidence"],
        "homework": "Write two pytest-style test functions for a normalise(text) helper (one positive, one negative case) and include a comment with the exact run command.",
    },
    "Test fixtures": {
        "theory": "**What it is**\nA fixture provides reusable test setup: @pytest.fixture functions whose result tests receive as a parameter.\n\n**Why it matters**\nShared setup lives in ONE place instead of copy-pasted into every test.\n\n**Watch out**\nEach test gets a FRESH fixture instance by default — tests never leak state into each other.",
        "code": "# import pytest at the top of the test file\n# @pytest.fixture\n# def sample_scores():\n#     return [82, 91, 58]\n#\n# def test_average(sample_scores):\n#     assert sum(sample_scores) / len(sample_scores) == 77\n\nsample_scores = [82, 91, 58]      # simulated fixture injection\nassert sum(sample_scores) / len(sample_scores) == 77\nprint('fixture-style check passed')",
        "questions": ["What does a fixture provide?", "How does a test receive fixture data?", "Why is per-test freshness important?"],
        "answers": ["Prepared setup data/resources injected into tests by name", "By declaring it as a test function parameter with the same name", "One test's mutations can't break another — isolation keeps failures honest"],
        "homework": "Define a fixture returning a sample dict profile and write two tests using it (one checking a field, one checking a computed value).",
    },
    "Logging": {
        "theory": "**What it is**\nlogging emits timestamped diagnostic events: debug(), info(), warning(), error(). Configure once with basicConfig.\n\n**Why it matters**\nUnlike prints, logs have severity levels and destinations — and can stay in production code.\n\n**Watch out**\nUse a module logger (__name__) and never log secrets.",
        "code": "import logging\nlogging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')\nlog = logging.getLogger(__name__)\n\ndef submit(code):\n    if not code.strip():\n        log.warning('empty submission received')\n        return False\n    log.info('submission checked: %d chars', len(code))\n    return True\n\nsubmit('print(1)')\nsubmit('   ')",
        "questions": ["Order the logging levels quietest to loudest", "Why prefer logging over print in real projects?", "Why use getLogger(__name__)?"],
        "answers": ["DEBUG, INFO, WARNING, ERROR, CRITICAL", "Levels, timestamps and configurable output; silence DEBUG without deleting code", "Log records then show which module emitted them"],
        "homework": "Configure logging, then write check_code(code) that logs info on success and warning on empty input; demonstrate both paths.",
    },
    "Configuration files": {
        "theory": "**What it is**\nConfig separates settings from logic: environment variables for secrets, files for structured settings.\n\n**Why it matters**\nSame code, different environments, zero edits — just different config values.\n\n**Watch out**\nNever hard-code credentials; read env vars with os.environ.get and fail loudly when critical ones are missing.",
        "code": "import os, json\n\ncfg = {\n    'daily_minutes': int(os.environ.get('STUDY_MINUTES', 60)),\n    'features': {'streaks': True},\n}\nprint(cfg['daily_minutes'])\nprint(json.dumps(cfg, indent=2))",
        "questions": ["What belongs in env vars vs config files?", "Why avoid hard-coded settings?", "How do you default missing env vars?"],
        "answers": ["Secrets and deployment endpoints in env vars; structured shared settings in files", "Every change would need a code edit; configs swap without touching logic", "os.environ.get('KEY', default_value)"],
        "homework": "Build an app_config dict combining two os.environ.get reads with defaults and one fixed setting, then pretty-print it.",
    },
    "Refactoring": {
        "theory": "**What it is**\nRefactoring restructures code WITHOUT changing behaviour: rename, extract function, remove duplication.\n\n**Why it matters**\nCode is read far more than written; small continuous cleanups prevent the big rewrite.\n\n**Watch out**\nOnly refactor with a verified behavioural baseline (tests) proving nothing changed.",
        "code": "# Before: duplicated logic\n# print(f'TOTAL {sum(s)} AVG {sum(s)/len(s)}')  ... twice ...\n\n# After: extracted helper\ndef average(scores):\n    return sum(scores) / len(scores)\n\ndef report(scores):\n    print(f'TOTAL {sum(scores)} AVG {average(scores)}')\n\nreport([80, 90, 70])",
        "questions": ["Define refactoring in one sentence", "Name two everyday refactorings", "What safety net must exist first?"],
        "answers": ["Improving internal structure while preserving observable behaviour exactly", "Extracting repeated code into a function; renaming for clarity", "Passing tests or another verified baseline"],
        "homework": "Refactor a duplicated calculation into a helper function, call it from two places, and print identical results proving behaviour didn't change.",
    },
    "Debugging workflow": {
        "theory": "**What it is**\nDebugging is a loop: REPRODUCE reliably → ISOLATE the smallest failing input → inspect → fix → VERIFY.\n\n**Why it matters**\nRandom print-spraying wastes time; a disciplined loop turns mystery bugs into checklists.\n\n**Watch out**\nIf you can't reproduce it, you can't confirm the fix.",
        "code": "def buggy_average(values):\n    total = 0\n    for index in range(len(values)):\n        total += values[index]\n    return total / len(values)            # crash when empty?\n\ntry:\n    print(buggy_average([]))              # ISOLATE smallest failing input\nexcept ZeroDivisionError as error:\n    print('isolated:', error)\nprint(buggy_average([2, 4]))              # VERIFY happy path",
        "questions": ["List the five steps of the debugging loop", "Why shrink the failing input?", "Where do temporary debug prints belong afterwards?"],
        "answers": ["Reproduce, isolate, inspect, fix, verify", "Smaller inputs reveal the true cause faster and become regression tests", "Nowhere — replace with logging or delete before committing"],
        "homework": "Intentionally break a working function (swap a comparison), reproduce the bug, isolate with a minimal call, fix it, and comment each debugging step.",
    },
})

# --- Algorithms and Math (shared phase 4) -----------------------------------
COMMON_TOPIC_LIBRARY.update({
    "Algorithm design": {
        "theory": "**What it is**\nDesign = plan before typing: state input/output, sketch steps in plain language, THEN translate to code.\n\n**Why it matters**\nTen minutes of design prevents an hour of rewrite.\n\n**Watch out**\nA step you can't explain simply usually hides a missing detail.",
        "code": "# PLAN: 1. walk days 1..n  2. keep even days\n#       3. minutes = day * 10  4. sum and return\ndef even_day_minutes(n):\n    total = 0\n    for day in range(1, n + 1):\n        if day % 2 == 0:\n            total += day * 10\n    return total\n\nprint(even_day_minutes(6))",
        "questions": ["Why write the plan before coding?", "What four things must a task statement fix?", "When is pseudocode most valuable?"],
        "answers": ["Logic mistakes surface on paper where edits are free", "Inputs, outputs, constraints and the transformation between them", "On multi-step logic with conditions or loops"],
        "homework": "Write pseudocode comments FIRST (four numbered steps) for a function counting odd numbers in a list, then implement and test it.",
    },
    "Big-O intuition": {
        "theory": "**What it is**\nBig-O describes how work GROWS with input size: O(1) constant, O(log n) halving, O(n) one pass, O(n²) nested passes.\n\n**Why it matters**\nAn O(n²) solution on 1M rows does a trillion comparisons — growth class beats micro-optimisations.\n\n**Watch out**\nConstants are ignored: 3n + 500 is still O(n).",
        "code": "def has_pair_sum(items, target):   # O(n^2): every pair\n    count = 0\n    for a in items:\n        for b in items:\n            count += 1             # operation counter\n            if a + b == target:\n                return True, count\n    return False, count\n\nprint(has_pair_sum([1, 3, 5, 7], 12))\nprint('single loop over n items is O(n)')",
        "questions": ["Classify a single loop over n items", "Classify a loop inside a loop over n items", "Why ignore constant factors?"],
        "answers": ["O(n) — linear growth", "O(n²) — quadratic; doubling input quadruples work", "Hardware changes constants; only the growth shape determines scalability"],
        "homework": "Write O(1), O(n) and O(n²) functions that each COUNT their operations, run all three on a small list, and print the counts side by side.",
    },
    "Arrays and linked lists": {
        "theory": "**What it is**\nArrays (Python lists) index in O(1). A linked list chains nodes pointing to the next — head insertion is O(1), reaching position k is O(k).\n\n**Why it matters**\nThe fast-access vs fast-insert trade-off drives data-structure choice everywhere.\n\n**Watch out**\nlist.insert(0, x) shifts every element — the slow operation lists hide.",
        "code": "class Node:\n    def __init__(self, value, nxt=None):\n        self.value = value\n        self.next = nxt\n\nchain = Node('mon', Node('tue', Node('wed')))\ncount = 0\ncursor = chain\nwhile cursor:\n    count += 1\n    cursor = cursor.next\nprint('linked list length:', count)\nprint('array access:', ['mon', 'tue', 'wed'][2])",
        "questions": ["Array access by index — complexity?", "Linked-list head insertion — complexity and why?", "Why is list.insert(0, x) slow?"],
        "answers": ["O(1)", "O(1): rewire two pointers regardless of length", "Every existing element shifts one place right"],
        "homework": "Build a three-node linked list manually, walk it counting nodes, then compare against direct list indexing in comments.",
    },
    "Stacks and queues": {
        "theory": "**What it is**\nStack = LIFO via list.append/.pop. Queue = FIFO via collections.deque append/popleft.\n\n**Why it matters**\nUndo history and expression parsing → stacks; schedulers and print queues → queues.\n\n**Watch out**\nlist.pop(0) is O(n); deque.popleft() is O(1).",
        "code": "from collections import deque\n\nstack = []\nstack.append('task1'); stack.append('task2')\nprint(stack.pop())               # task2 — last in, first out\n\nqueue = deque(['student_a', 'student_b'])\nqueue.append('student_c')\nprint(queue.popleft())           # student_a — first in, first out",
        "questions": ["Which end does a stack operate on?", "Which deque methods form a FIFO queue?", "Why not use list.pop(0) for queues?"],
        "answers": ["The tail of the list — both append and pop happen there", "append() to enqueue, popleft() to dequeue", "It removes from the front but shifts all remaining elements — O(n) per operation"],
        "homework": "Push three tasks onto a stack and pop them all, then enqueue them into a deque and popleft all; print both orders to show LIFO vs FIFO.",
    },
    "Hash tables": {
        "theory": "**What it is**\nA hash table maps keys to slots via hash(key). Python dicts ARE hash tables — average lookup/insert/delete are O(1).\n\n**Why it matters**\nFast lookups power caches, indexes and counters.\n\n**Watch out**\nKeys must be immutable because their hash must never change.",
        "code": "marks = {'riya': 85, 'aarav': 92}\nmarks['kabir'] = 78                       # O(1) insert\nprint('riya' in marks)                    # O(1) lookup\nprint(marks.get('missing', 0))            # safe read\nprint(hash('python') == hash('python'))   # stable within a run",
        "questions": ["Average dict lookup speed vs scanning a list?", "Why must dict keys be immutable?", "What is a collision?"],
        "answers": ["Roughly O(1) versus O(n)", "Changing a key would move its storage slot, losing the entry", "Two different keys hashing to the same slot — handled internally while staying fast on average"],
        "homework": "Build a topic-to-minutes dict for four topics, demonstrate O(1)-style lookup, and use .get safely on a missing key.",
    },
    "Trees": {
        "theory": "**What it is**\nTrees nest nodes hierarchically: one root, branches, leaves. Nested dicts model them perfectly.\n\n**Why it matters**\nFile systems, org charts and DOM are trees; traversal is how you process them.\n\n**Watch out**\nCycles break naive traversals — trees have none by definition, general graphs need visited-tracking.",
        "code": "course = {\n    'name': 'Python',\n    'children': [\n        {'name': 'basics', 'children': []},\n        {'name': 'loops', 'children': [{'name': 'while', 'children': []}]},\n    ],\n}\ndef print_tree(node, depth=0):\n    print('  ' * depth + node['name'])\n    for child in node['children']:\n        print_tree(child, depth + 1)\n\nprint_tree(course)",
        "questions": ["Define root, leaf and depth", "Why do nested dicts fit trees so well?", "What breaks if a 'tree' contains a cycle?"],
        "answers": ["Root has no parent; leaf has no children; depth = distance from root", "Each child is itself the same structure — matching recursion naturally", "Traversal never terminates without visited-set protection"],
        "homework": "Build a three-level course tree as nested dicts, write print_tree exactly as shown, add one more leaf, then print.",
    },
    "Graphs": {
        "theory": "**What it is**\nGraphs are nodes + edges; adjacency dicts ({node: [neighbors]}) are the simplest representation. BFS explores level-by-level using a queue.\n\n**Why it matters**\nNetworks, routes and dependencies are graphs; BFS finds shortest paths in unweighted ones.\n\n**Watch out**\nAlways track visited nodes — otherwise cycles loop forever.",
        "code": "from collections import deque\n\ngraph = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}\ndef bfs(start):\n    seen, order, queue = {start}, [], deque([start])\n    while queue:\n        node = queue.popleft()\n        order.append(node)\n        for neighbor in graph[node]:\n            if neighbor not in seen:\n                seen.add(neighbor)\n                queue.append(neighbor)\n    return order\n\nprint(bfs('a'))",
        "questions": ["How is a graph represented here?", "Which data structure powers BFS?", "Why track visited nodes?"],
        "answers": ["As an adjacency mapping: each node maps to its neighbour list", "A queue — first discovered, first explored", "Graphs can contain cycles; without marking, traversal revisits nodes forever"],
        "homework": "Add node 'e' reachable via 'b', rerun bfs('a'), and verify 'e' appears after 'd' in the printed order.",
    },
})

COMMON_TOPIC_LIBRARY.update({
    "Searching": {
        "theory": "**What it is**\nLinear search checks every item — O(n), works unsorted. Binary search halves the range each probe — O(log n) but REQUIRES sorted data.\n\n**Why it matters**\n1M sorted items need ~20 binary probes instead of up to a million linear checks.\n\n**Watch out**\nOff-by-one bugs live in low/high updates. Keep the invariant: the target, if present, lies within [low, high].",
        "code": "def binary_search(sorted_items, target):\n    low, high = 0, len(sorted_items) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if sorted_items[mid] == target:\n            return mid\n        if sorted_items[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\nprint(binary_search([10, 20, 30, 40, 50], 40))\nprint(binary_search([10, 20, 30, 40, 50], 35))",
        "questions": ["Precondition for binary search?", "Probes needed for 1,000,000 sorted items?", "What invariant keeps binary search correct?"],
        "answers": ["The collection must already be sorted", "About log2(1e6) ≈ 20", "The target, if present, always remains inside [low, high]; mid is excluded after testing"],
        "homework": "Implement binary_search, find targets 30 and 45 in a sorted list printing index or -1, and count probes with a variable.",
    },
    "Sorting": {
        "theory": "**What it is**\nsorted() returns a new ordered list; list.sort() orders in place. key= chooses what to sort BY; sorts are STABLE.\n\n**Why it matters**\nRankings and leaderboards all start with correct sorting via key functions.\n\n**Watch out**\nSorting mixed types raises TypeError; decide the key explicitly.",
        "code": "rows = [('riya', 85), ('aarav', 92), ('kabir', 85)]\nby_marks = sorted(rows, key=lambda row: row[1], reverse=True)\nprint(by_marks)\nleaderboard = sorted(rows, key=lambda row: (-row[1], row[0]))\nprint(leaderboard)      # stable: riya before kabir at 85",
        "questions": ["sorted() vs .sort()?", "What does key=lambda row: row[1] do?", "What does stable sorting preserve?"],
        "answers": ["sorted returns a new list; .sort() mutates and returns None", "Uses the second tuple element (the mark) as comparison value", "The relative order of equal elements"],
        "homework": "Sort students by mark descending AND ties by name ascending using one key lambda returning a tuple; print the leaderboard.",
    },
    "Probability basics": {
        "theory": "**What it is**\nProbability = favourable outcomes / total outcomes (0 to 1). Simulation approximates it by counting frequencies over many random trials.\n\n**Why it matters**\nSimulations verify probability reasoning when maths gets hairy.\n\n**Watch out**\nFew trials give noisy estimates; convergence appears only with thousands of runs.",
        "code": "import random\n\ntrials = 10000\nheads = sum(1 for _ in range(trials) if random.random() < 0.5)\nestimate = heads / trials\nprint(f'estimated P(heads) = {estimate}')\nprint(f'error vs theory 0.5 = {abs(estimate - 0.5)}')",
        "questions": ["Formula for simple probability?", "How does simulation estimate probability?", "Why might 10 trials disagree strongly with theory?"],
        "answers": ["Favourable outcomes divided by all equally likely outcomes", "Run the experiment many times; success frequency approximates the probability", "Small samples are noisy — error shrinks roughly as 1/sqrt(trials)"],
        "homework": "Simulate rolling two dice 10,000 times; estimate P(sum == 7), print it next to the theoretical 6/36, and comment on the difference.",
    },
    "Statistics basics": {
        "theory": "**What it is**\nMean = average; median = middle value (robust to outliers); std-dev measures dispersion around the mean.\n\n**Why it matters**\nOne billionaire moves the mean but barely the median — choosing the right summary prevents misleading claims.\n\n**Watch out**\nVariance averages SQUARED deviations; std-dev squares back to normal units.",
        "code": "scores = [55, 60, 65, 70, 300]\nmean = sum(scores) / len(scores)\nordered = sorted(scores)\nmedian = ordered[len(ordered) // 2]\nvariance = sum((s - mean) ** 2 for s in scores) / len(scores)\nprint(mean, median)                  # outlier pulls mean, not median\nprint(round(variance ** 0.5, 1))     # std deviation",
        "questions": ["Compute median for [1, 9, 5]", "Why prefer median with outliers?", "Relation between variance and std dev?"],
        "answers": ["Sort → [1, 5, 9] → median is 5", "Mean chases extreme values; median stays at the middle rank", "Std dev is the square root of variance — same units as the data"],
        "homework": "Given a scores list with one absurd outlier, compute mean, median and std-dev manually (no statistics module), and print which summary the outlier distorts more.",
    },
    "Vectors": {
        "theory": "**What it is**\nA vector is a list of numbers: addition is element-wise; the dot product sums pairwise products (measuring alignment).\n\n**Why it matters**\nEmbeddings, ML features and game physics treat data as vectors.\n\n**Watch out**\nPython's + on lists CONCATENATES ([1,2]+[3,4] is [1,2,3,4]) — element-wise addition must be computed.",
        "code": "v = [1, 2]\nw = [3, 4]\nadded = [a + b for a, b in zip(v, w)]     # element-wise!\ndot = sum(a * b for a, b in zip(v, w))\nmagnitude = sum(a * a for a in v) ** 0.5\nprint(added, dot, round(magnitude, 3))",
        "questions": ["Result of element-wise [1,2]+[3,4]?", "What does the dot product roughly measure?", "Why can't you use + directly for vector addition?"],
        "answers": ["[4, 6] — computed pairwise", "Alignment/similarity of direction (large positive = aligned)", "Python concatenates lists instead of adding pairwise"],
        "homework": "Write vector_add(u, v) and dot(u, v) using zip, assert dot([1,0],[0,1]) == 0 (perpendicular!), and print all results.",
    },
    "Matrices": {
        "theory": "**What it is**\nA matrix is a list of equal-length rows; element (i, j) is m[i][j]; transpose flips rows and columns.\n\n**Why it matters**\nTables, images and transformations are matrices.\n\n**Watch out**\n[[0]*cols]*rows replicates the SAME row object — use comprehensions instead.",
        "code": "m = [[1, 2, 3],\n     [4, 5, 6]]\ntranspose = [[row[col] for row in m] for col in range(len(m[0]))]\nprint(transpose)                 # [[1,4],[2,5],[3,6]]\nwrong = [[0] * 3] * 2\nwrong[0][0] = 9\nprint(wrong)                     # both rows changed!",
        "questions": ["Access element at row i, column j?", "What does transpose do?", "Why is [[0]*c]*r dangerous?"],
        "answers": ["m[i][j] — outer index selects the row, inner the column", "Exchanges rows and columns: (i,j) moves to (j,i)", "It repeats one row reference r times, so editing any row edits all"],
        "homework": "Transpose a 2x3 matrix with a comprehension, print dimensions before/after, and demonstrate the shared-row trap in a comment.",
    },
    "Functions and graphs": {
        "theory": "**What it is**\nSampling f(x) over a range reveals shape: growth, peaks, symmetry — even as an ASCII plot.\n\n**Why it matters**\nSAMPLE → MAP → RENDER is the core skill behind every charting library.\n\n**Watch out**\nCoarse sampling hides spikes; resolution matters even in text plots.",
        "code": "def f(x):\n    return x * x\n\nfor x in range(-3, 4):\n    value = f(x)\n    bar = '#' * value\n    print(f'{x:>3} | {bar} ({value})')",
        "questions": ["What does sampling a function mean?", "Why does x*x give symmetric output for negative x?", "What happens with a coarser step?"],
        "answers": ["Evaluating it at many discrete points to approximate its behaviour", "Squaring discards sign: (-n)^2 equals n^2", "Fewer samples — narrow features disappear"],
        "homework": "Plot f(x)=x*x as ASCII bars for x=-5..5, then note in comments where abs(x) would agree or differ.",
    },
    "Problem-solving project": {
        "theory": "**What it is**\nThe capstone method: decompose into named sub-functions, build each with checks, assemble, document honestly.\n\n**Why it matters**\nReal projects are ten boring functions composed cleanly, not one clever function.\n\n**Watch out**\nDefine inputs/outputs of EVERY piece before writing ANY piece.",
        "code": "def read_rows():                      # piece 1: input\n    return [['maths', 85], ['code', 92]]\n\ndef top_row(rows):                    # piece 2: logic\n    return max(rows, key=lambda row: row[1])\n\ndef report(row):                      # piece 3: output\n    return f'best subject: {row[0]} ({row[1]})'\n\nprint(report(top_row(read_rows())))   # assembly",
        "questions": ["Name the decomposition stages used here", "Why test pieces before assembling?", "What belongs in honest documentation?"],
        "answers": ["Input handling, core logic, presentation, then composition", "Failures localize to a tiny function instead of hiding inside a big program", "What it does, how to run it, known limitations"],
        "homework": "Decompose a mini grade-reporter into three functions (input, best-subject logic, formatted report), compose them, and print the final line.",
    },
})

# ---------------------------------------------------------------------------
# Track-phase worked-example templates. Each produces a runnable, pure-Python
# lesson example themed for its phase, so track-specific days carry real
# domain flavour. "{topic}" is substituted literally via str.replace (never
# str.format, so braces inside examples stay safe).
# ---------------------------------------------------------------------------
PHASE_EXAMPLE_TEMPLATES: dict[str, str] = {
    "Scientific Python": (
        "# {topic} — scientific computing drill (pure Python)\n"
        "data = [2.5, 3.1, 2.8, 3.4, 3.0]\n"
        "mean = sum(data) / len(data)\n"
        "centered = [round(value - mean, 3) for value in data]\n"
        "print('{topic}: mean =', round(mean, 3))\n"
        "print('{topic}: centered =', centered)\n"
        "print('{topic}: max deviation =', round(max(abs(v) for v in centered), 3))"
    ),
    "Machine Learning": (
        "# {topic} — nearest-neighbour classifier by hand\n"
        "training = [(1, 45), (3, 62), (5, 78), (7, 91)]   # (study_hours, score)\n"
        "def predict(hours):\n"
        "    best = min(training, key=lambda row: abs(row[0] - hours))\n"
        "    return best[1]\n"
        "print('{topic}: predict(4h) =', predict(4))\n"
        "errors = [abs(predict(h) - s) for h, s in training]\n"
        "print('{topic}: mean training error =', round(sum(errors) / len(errors), 2))"
    ),
    "Deep Learning": (
        "# {topic} — one artificial neuron computed manually\n"
        "inputs = [0.6, 0.2]\n"
        "weights = [0.4, 0.7]\n"
        "bias = 0.1\n"
        "z = sum(i * w for i, w in zip(inputs, weights)) + bias\n"
        "relu = max(0.0, z)\n"
        "print('{topic}: weighted sum z =', round(z, 3))\n"
        "print('{topic}: after ReLU =', relu)"
    ),
    "Language and Transformers": (
        "# {topic} — turning text into vectors\n"
        "sentence = 'students learn attention'.split()\n"
        "vocab = sorted(set(sentence))\n"
        "vectors = {word: [int(w == word) for w in vocab] for word in sentence}\n"
        "print('vocabulary =', vocab)\n"
        "for word, vector in vectors.items():\n"
        "    print(word, '=', vector)"
    ),
    "Reasoning and Agents": (
        "# {topic} — sense, decide, act loop\n"
        "state = {'position': 0, 'goal': 3}\n"
        "actions = []\n"
        "while state['position'] < state['goal']:\n"
        "    actions.append('step-right')\n"
        "    state['position'] += 1\n"
        "print('{topic}: action trace =', actions)\n"
        "print('{topic}: goal reached =', state['position'] == state['goal'])"
    ),
    "Research Practice": (
        "# {topic} — reproducible mini-experiment\n"
        "import random\n"
        "random.seed(42)                     # fixed seed = reproducible run\n"
        "baseline = [random.randint(50, 70) for _ in range(5)]\n"
        "treatment = [random.randint(55, 80) for _ in range(5)]\n"
        "avg_b = sum(baseline) / len(baseline)\n"
        "avg_t = sum(treatment) / len(treatment)\n"
        "print('{topic}: baseline avg =', round(avg_b, 1), '| treatment avg =', round(avg_t, 1))\n"
        "print('{topic}: observed lift =', round(avg_t - avg_b, 1), '(within noise?)')"
    ),
    "AI Research Capstone": (
        "# {topic} — experiment design scaffold\n"
        "design = {\n"
        "    'question': 'Does daily practice raise placement scores?',\n"
        "    'baseline': 'single long weekend session',\n"
        "    'metric': 'average score after 14 days',\n"
        "}\n"
        "for field, value in design.items():\n"
        "    print('{topic}:', field, '->', value)\n"
        "print('{topic}: design complete =', all(design.values()))"
    ),
    "Data Workflow": (
        "# {topic} — parsing and cleaning raw rows\n"
        "raw_rows = ['riya,85,python', 'aarav,,maths', 'kabir,78,code']\n"
        "records = []\n"
        "for row in raw_rows:\n"
        "    name, score, subject = row.split(',')\n"
        "    records.append({'name': name, 'score': int(score) if score else None})\n"
        "clean = [record for record in records if record['score'] is not None]\n"
        "print('{topic}: parsed =', records)\n"
        "print('{topic}: kept after cleaning =', clean)"
    ),
    "Statistics": (
        "# {topic} — summarising a sample honestly\n"
        "sample = [55, 60, 65, 70, 300]          # contains an outlier\n"
        "mean = sum(sample) / len(sample)\n"
        "ordered = sorted(sample)\n"
        "median = ordered[len(ordered) // 2]\n"
        "variance = sum((x - mean) ** 2 for x in sample) / len(sample)\n"
        "print('{topic}: mean =', round(mean, 1), '| median =', median)\n"
        "print('{topic}: std dev =', round(variance ** 0.5, 1))"
    ),
    "Visualization": (
        "# {topic} — ASCII bar chart of study marks\n"
        "marks = {'riya': 85, 'aarav': 92, 'kabir': 78}\n"
        "for name, mark in marks.items():\n"
        "    bar = '#' * (mark // 5)\n"
        "    print(f'{name:>6} | {bar} {mark}')\n"
        "print('tallest bar belongs to', max(marks, key=marks.get))"
    ),
    "Predictive Modelling": (
        "# {topic} — fitting a trend line by least squares\n"
        "hours = [1, 2, 3, 4]\n"
        "scores = [52, 58, 65, 72]\n"
        "mean_x = sum(hours) / len(hours)\n"
        "mean_y = sum(scores) / len(scores)\n"
        "slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(hours, scores)) / sum((x - mean_x) ** 2 for x in hours)\n"
        "intercept = mean_y - slope * mean_x\n"
        "print('model -> score =', round(slope, 2), '* hours +', round(intercept, 2))\n"
        "print('predicted score at 5 hours =', round(slope * 5 + intercept, 1))"
    ),
}

PHASE_EXAMPLE_TEMPLATES.update({
    "Evaluation and Deployment": (
        "# {topic} — confusion-matrix metrics by hand\n"
        "truth =       [1, 0, 1, 1, 0, 0, 1]\n"
        "predicted =   [1, 0, 0, 1, 0, 1, 1]\n"
        "tp = sum(p == 1 and t == 1 for p, t in zip(predicted, truth))\n"
        "fp = sum(p == 1 and t == 0 for p, t in zip(predicted, truth))\n"
        "tn = sum(p == 0 and t == 0 for p, t in zip(predicted, truth))\n"
        "accuracy = (tp + tn) / len(truth)\n"
        "precision = tp / (tp + fp) if tp + fp else 0.0\n"
        "print('{topic}: accuracy =', round(accuracy, 2), '| precision =', round(precision, 2))"
    ),
    "Applied Data Projects": (
        "# {topic} — project stage tracker\n"
        "stages = ['question', 'collect', 'clean', 'analyse', 'communicate']\n"
        "done = {'question': True, 'collect': True, 'clean': False}\n"
        "blocked = [stage for stage in stages if not done.get(stage)]\n"
        "print('{topic}: next stage up =', blocked[0] if blocked else 'project shipped!')\n"
        "print('{topic}: completed count =', len(stages) - len(blocked), '/', len(stages))"
    ),
    "Data Science Capstone": (
        "# {topic} — capstone charter\n"
        "charter = {\n"
        "    'question': 'Which study habit predicts higher marks?',\n"
        "    'data_needed': 'daily minutes + weekly test score',\n"
        "    'deliverable': 'one chart plus one recommendation',\n"
        "}\n"
        "for field, value in charter.items():\n"
        "    print('{topic}:', field, '->', value)\n"
        "print('{topic}: ready to collect data =', all(charter.values()))"
    ),
    "Web Foundations": (
        "# {topic} — an HTTP request/response cycle in miniature\n"
        "request = {'method': 'GET', 'path': '/courses'}\n"
        "reasons = {200: 'OK', 404: 'Not Found'}\n"
        "pages = {'/': 'home page', '/courses': 'course list'}\n"
        "def serve(req):\n"
        "    body = pages.get(req['path'])\n"
        "    status = 200 if body else 404\n"
        "    return {'status': status, 'reason': reasons[status], 'body': body}\n"
        "response = serve(request)\n"
        "print('{topic}:', request['method'], request['path'], '->', response['status'], response['reason'])"
    ),
    "FastAPI APIs": (
        "# {topic} — routing and JSON responses simulated\n"
        "routes = {}\n"
        "def route(method, path):\n"
        "    def register(handler):\n"
        "        routes[(method, path)] = handler\n"
        "        return handler\n"
        "    return register\n"
        "@route('GET', '/topics')\n"
        "def list_topics():\n"
        "    return {'items': ['loops', 'strings']}\n"
        "handler = routes[('GET', '/topics')]\n"
        "print('{topic}: response =', handler())"
    ),
    "Databases": (
        "# {topic} — SQL concepts on list-of-dict rows\n"
        "table = [\n"
        "    {'id': 1, 'name': 'riya', 'xp': 120},\n"
        "    {'id': 2, 'name': 'aarav', 'xp': 90},\n"
        "]\n"
        "def select_where(rows, column, value):     # like SELECT ... WHERE\n"
        "    return [row for row in rows if row[column] == value]\n"
        "print('{topic}: WHERE id = 1 ->', select_where(table, 'id', 1))\n"
        "table.append({'id': 3, 'name': 'kabir', 'xp': 75})    # INSERT\n"
        "print('{topic}: rows after INSERT =', len(table))"
    ),
    "Full-stack Features": (
        "# {topic} — validating a form submission like an API would\n"
        "payload = {'email': 'AARAV@X.com ', 'age': '17'}\n"
        "errors = []\n"
        "email = payload['email'].strip().lower()\n"
        "if '@' not in email:\n"
        "    errors.append('valid email required')\n"
        "try:\n"
        "    age = int(payload['age'])\n"
        "except ValueError:\n"
        "    errors.append('age must be a number')\n"
        "print('{topic}: cleaned email =', email)\n"
        "print('{topic}: validation result =', errors or 'accepted')"
    ),
    "Quality and Security": (
        "# {topic} — sanitising hostile input\n"
        "unsafe_comment = \"<script>alert('x')</script> nice site!\"\n"
        "allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !.,')\n"
        "sanitised = ''.join(ch for ch in unsafe_comment if ch in allowed)\n"
        "assert '<' not in sanitised, 'angle brackets must never survive'\n"
        "print('{topic}: safety assertion passed')"
    ),
    "Deployment and Collaboration": (
        "# {topic} — pre-release checklist gate\n"
        "checklist = {\n"
        "    'tests pass': True,\n"
        "    'secrets moved to environment variables': True,\n"
        "    'database backup taken': False,\n"
        "}\n"
        "blocking = [item for item, ok in checklist.items() if not ok]\n"
        "verdict = 'YES' if not blocking else 'NO — blocked by ' + ', '.join(blocking)\n"
        "print('{topic}: can deploy?', verdict)"
    ),
    "Web Development Capstone": (
        "# {topic} — feature inventory for the final build\n"
        "features = {\n"
        "    'user registration': 'planned',\n"
        "    'course dashboard': 'built',\n"
        "    'progress tracking API': 'built',\n"
        "}\n"
        "remaining = [name for name, status in features.items() if status != 'built']\n"
        "print('{topic}: still to build =', remaining or 'nothing — ship it!')"
    ),
})


def _phase_template_code(phase_title: str, topic: str) -> str | None:
    template = PHASE_EXAMPLE_TEMPLATES.get(phase_title)
    if template is None:
        return None
    return template.replace("{topic}", topic)


# Fully authored Data Science track content (all 105 track-phase topics).
from .ds_topic_library import DS_TOPIC_LIBRARY  # noqa: E402


def _generic_example_code(topic: str, day: int) -> str:
    """Fallback worked example when no authored entry or template exists."""
    safe = "day_" + str(day)
    return (
        f"def {safe}(example):\n"
        f"    \"\"\"Worked micro-example for {topic}.\"\"\"\n"
        f"    print('concept:', '{topic}')\n"
        f"    print('input :', example)\n"
        f"    result = example\n"
        f"    print('output:', result)\n"
        f"    return result\n\n"
        f"{safe}('first attempt')"
    )


def _layered_questions(topic: str) -> list[str]:
    """Three questions moving from recall to transfer."""
    return [
        f"What problem does {topic} solve, and in which situation would you avoid it?",
        f"In today's worked example, which exact line demonstrates {topic}, and what changes if you delete it?",
        f"How would you modify the example so a classmate could watch {topic} fail on purpose?",
    ]


def _layered_answers(objective: str) -> list[str]:
    return [
        objective,
        "The line carrying the core operation — removing it should change the output or raise an error.",
        "Feed it an edge case (empty input, zero, or a wrong type) so the failure becomes visible, then explain why it happened.",
    ]


_FALLBACK_HOMEWORK = (
    "Write a program of at least five non-empty lines demonstrating today's concept: "
    "define a function, call it on two different inputs, print both results, and add a "
    "one-line comment describing what changed between the runs."
)


def extended_curriculum(slug: str):
    """Return Days 15–180 for one launch programme.

    Shared-phase topics draw on COMMON_TOPIC_LIBRARY (fully authored theory,
    examples, questions and homework). Track-phase topics use
    PHASE_EXAMPLE_TEMPLATES for domain-flavoured worked examples plus layered
    questions. The tuple layout matches seed.py exactly and always yields 166
    entries (Days 15–179 + Day 180 reflection), so each track totals 180 days.
    """
    entries = []
    day = 15
    for phase_title, domain, phase_goal, topics in COMMON_180_PHASES + TRACK_180_PHASES[slug]:
        for topic in topics:
            authored = COMMON_TOPIC_LIBRARY.get(topic) or (
                DS_TOPIC_LIBRARY if slug == "data-science" else {}
            ).get(topic)
            template_code = _phase_template_code(phase_title, topic)

            if authored:
                code = authored["code"]
                theory = authored["theory"]
                questions = list(authored["questions"])
                answers = list(authored["answers"])
                homework = authored["homework"]
            elif template_code:
                code = template_code
                theory = (
                    f"**Today: {topic}**\n\n{phase_goal}\n\n"
                    f"**Where this fits**\nThis day belongs to the **{phase_title}** phase of your "
                    f"programme ({domain}). By the end you should be able to explain {topic} to a "
                    "classmate without notes.\n\n"
                    "**Study protocol (60 minutes)**\n"
                    "1. Read the worked example and predict its output before running it.\n"
                    "2. Change exactly one value and predict again — either way you learn.\n"
                    "3. Write today's practice from scratch while explaining choices in comments."
                )
                questions = _layered_questions(topic)
                answers = _layered_answers(f"Explain and apply {topic} in a small, testable Python example.")
                homework = (
                    f"Demonstrate **{topic}** in a {domain} context in at least five non-empty lines: "
                    "define a function, run it on two different inputs, print both results, and comment "
                    "which line is the heart of the demonstration."
                )
            else:
                code = _generic_example_code(topic, day)
                theory = (
                    f"**Today: {topic}**\n\n{phase_goal}\n\n"
                    "**Study protocol (60 minutes)**\n"
                    "1. Run the example and predict the output first.\n"
                    "2. Change one value and predict again.\n"
                    "3. Rewrite today's practice from memory."
                )
                questions = _layered_questions(topic)
                answers = _layered_answers(f"Explain and apply {topic} in a small, testable Python example.")
                homework = _FALLBACK_HOMEWORK

            objective = f"Explain and apply {topic} in a small, testable Python example."
            entries.append((f"{phase_title}: {topic}", domain, objective, code, homework,
                            ["def ", "print("], theory))
            day += 1
    # 11 phases × 15 days plus Day 180 capstone reflection.
    entries.append(("180-day capstone reflection", "Capstone",
                    "Review your final project, explain your design choices, and plan the next learning milestone.",
                    "def reflect(project):\n    print('What I built:', project)\n\nreflect('my 180-day capstone')",
                    "Write a function that prints your capstone name, one skill you learned, and one next-step goal.",
                    ["def ", "print("],
                    "**Finish line**\n\nA strong capstone includes working code, clear documentation, honest limitations and an explanation in your own words."))
    return entries
