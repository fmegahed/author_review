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

# Common review fields (same across all tracks)
COMMON_FIELDS = [
    {"key": "summary", "label": "AI Summary", "question": "Is this AI Summary correct?"},
    {"key": "key_results", "label": "Key Results", "question": "Are these Key Results correct?"},
    {"key": "key_equations", "label": "Key Equations", "question": "Are these Key Equations correct?", "mathjax": True},
    {"key": "future_work_unstated", "label": "Unstated Future Work", "question": "Is this Unstated Future Work reasonable?"},
]
