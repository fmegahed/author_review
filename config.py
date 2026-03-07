import os

# --- Environment variables ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/author_review")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# --- GitHub raw CSV base URL ---
CSV_BASE_URL = "https://raw.githubusercontent.com/fmegahed/hf_arxiv_control_charts/main/data"

# --- CSV cache TTL in seconds ---
CSV_CACHE_TTL = 3600  # 1 hour

# --- Track configuration ---
TRACKS = {
    "spc": {
        "label": "Control Charts (SPC)",
        "short_label": "SPC",
        "color": "#C41230",
        "metadata_csv": "spc_arxiv_metadata.csv",
        "factsheet_csv": "spc_factsheet.csv",
        "relevance_field": "is_spc_paper",
    },
    "exp_design": {
        "label": "Experimental Design (DOE)",
        "short_label": "DOE",
        "color": "#1B9E77",
        "metadata_csv": "exp_design_arxiv_metadata.csv",
        "factsheet_csv": "exp_design_factsheet.csv",
        "relevance_field": "is_exp_design_paper",
    },
    "reliability": {
        "label": "Reliability Engineering",
        "short_label": "Reliability",
        "color": "#D95F02",
        "metadata_csv": "reliability_arxiv_metadata.csv",
        "factsheet_csv": "reliability_factsheet.csv",
        "relevance_field": "is_reliability_paper",
    },
}

# --- Track-specific field mappings ---
# Maps position (track_field_1..4) to actual CSV column names per track
TRACK_FIELD_MAPPINGS = {
    "spc": {
        "track_field_1": {"column": "chart_family", "label": "Chart Family"},
        "track_field_2": {"column": "chart_statistic", "label": "Chart Statistic"},
        "track_field_3": {"column": "phase", "label": "Phase"},
        "track_field_4": {"column": "application_domain", "label": "Application Domain"},
    },
    "exp_design": {
        "track_field_1": {"column": "design_type", "label": "Design Type"},
        "track_field_2": {"column": "design_objective", "label": "Design Objective"},
        "track_field_3": {"column": "optimality_criterion", "label": "Optimality Criterion"},
        "track_field_4": {"column": "number_of_factors", "label": "Number of Factors"},
    },
    "reliability": {
        "track_field_1": {"column": "reliability_topic", "label": "Reliability Topic"},
        "track_field_2": {"column": "modeling_approach", "label": "Modeling Approach"},
        "track_field_3": {"column": "data_type", "label": "Data Type"},
        "track_field_4": {"column": "maintenance_policy", "label": "Maintenance Policy"},
    },
}

# --- Valid categories for track fields (excluding "Other") ---
# Used to show context when a field is classified as "Other"
FIELD_CATEGORIES = {
    "chart_family": ["Univariate", "Multivariate", "Self-starting", "Profile monitoring", "Image-based monitoring", "Functional data analysis", "Bayesian", "Nonparametric", "High-dimensional"],
    "chart_statistic": ["Shewhart", "CUSUM", "EWMA", "Hotelling T-squared", "MEWMA", "MCUSUM", "GLR", "Change-point", "Machine learning-based"],
    "phase": ["Phase I", "Phase II", "Both"],
    "application_domain": ["Manufacturing", "Semiconductor/electronics", "Healthcare/medical", "Pharmaceutical", "Finance/economics", "Environmental monitoring", "Network/cybersecurity", "Service industry", "Food/agriculture", "Energy/utilities", "Transportation/logistics", "Theoretical/simulation only"],
    "design_type": ["Factorial (full)", "Factorial (fractional)", "Response surface", "Mixture", "Split-plot", "Optimal design", "Screening", "Definitive screening", "Supersaturated", "Robust parameter design", "Sequential/adaptive", "Computer experiment", "Bayesian design"],
    "design_objective": ["Parameter estimation", "Screening", "Optimization", "Model discrimination", "Prediction", "Robustness", "Cost reduction"],
    "optimality_criterion": ["D-optimal", "A-optimal", "I-optimal (IV-optimal)", "G-optimal", "E-optimal", "V-optimal", "Bayesian D-optimal", "Bayesian A-optimal", "Compound criterion", "Space-filling", "Minimax/Maximin", "Not applicable"],
    "reliability_topic": ["Life distribution modeling", "Degradation modeling", "RUL prediction", "Failure mode analysis", "Accelerated testing", "Maintenance optimization", "System reliability", "Warranty analysis", "Reliability growth", "Software reliability", "Network/infrastructure reliability"],
    "modeling_approach": ["Parametric (Weibull, etc.)", "Nonparametric/Semi-parametric", "Stochastic process", "Physics-based", "ML-based", "Bayesian", "Hybrid/Ensemble", "Simulation-based"],
    "data_type": ["Complete lifetime data", "Right-censored", "Interval-censored", "Left-censored", "Degradation measurements", "Event/count data", "Sensor/condition monitoring", "Mixture of types", "Simulated only"],
    "maintenance_policy": ["Age-based", "Block replacement", "Condition-based", "Predictive", "Opportunistic", "Group replacement", "Imperfect maintenance", "Not applicable"],
}

# Common review fields (same across all tracks)
COMMON_FIELDS = [
    {"key": "summary", "label": "AI Summary", "question": "Is this AI Summary correct?"},
    {"key": "key_results", "label": "Key Results", "question": "Are these Key Results correct?"},
    {"key": "key_equations", "label": "Key Equations", "question": "Are these Key Equations correct?", "mathjax": True},
    {"key": "future_work_unstated", "label": "Unstated Future Work", "question": "Does the text below contain future work not discussed in the paper that is reasonable?"},
]
