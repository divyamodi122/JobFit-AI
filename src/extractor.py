import re
import PyPDF2



SKILLS_DB = {
    # Programming Languages
    "python", "r", "java", "scala", "julia", "c++", "c#", "javascript",

    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "transfer learning",
    "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch",
    "xgboost", "lightgbm", "catboost", "random forest", "neural network",
    "bert", "lstm", "cnn", "rnn", "transformer",

    # Data & Stats
    "pandas", "numpy", "scipy", "statistics", "regression", "classification",
    "clustering", "time series", "feature engineering", "data wrangling",
    "exploratory data analysis", "eda",

    # Visualization
    "matplotlib", "seaborn", "plotly", "tableau", "power bi", "looker",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis",
    "bigquery", "snowflake", "hive",

    # Big Data
    "spark", "hadoop", "kafka", "airflow", "dbt", "etl", "data pipeline",

    # Cloud
    "aws", "gcp", "azure", "s3", "ec2", "sagemaker", "lambda",
    "google colab", "databricks",

    # Tools & DevOps
    "git", "github", "docker", "kubernetes", "fastapi", "flask",
    "streamlit", "rest api", "api", "linux", "bash",

    # Other
    "excel", "nltk", "spacy", "opencv", "mlflow", "jupyter",
}



def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract plain text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[extractor] PDF read error: {e}")
    return text


def extract_skills_from_text(text: str) -> set:
    """Extract skills from any plain text string."""
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_DB:
        # Use word-boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def extract_skills_from_pdf(pdf_path: str) -> set:
    """Extract skills directly from a PDF file."""
    text = extract_text_from_pdf(pdf_path)
    return extract_skills_from_text(text)