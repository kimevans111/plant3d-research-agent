"""CSV data loading for E-commerce Ops Agent Mini."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SAMPLE_DATA_DIR = Path(__file__).resolve().parent / "sample_data"


def load_products(path: Path | str | None = None) -> pd.DataFrame:
    """Load products CSV and return a DataFrame with normalized types."""
    file_path = Path(path) if path else SAMPLE_DATA_DIR / "products.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Products data not found: {file_path}")
    df = pd.read_csv(file_path)
    df["conversion_rate"] = pd.to_numeric(df["conversion_rate"], errors="coerce")
    df["refund_rate"] = pd.to_numeric(df["refund_rate"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce")
    df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df["stock"] = pd.to_numeric(df["stock"], errors="coerce")
    return df


def load_campaigns(path: Path | str | None = None) -> pd.DataFrame:
    """Load campaigns CSV and return a DataFrame with normalized types."""
    file_path = Path(path) if path else SAMPLE_DATA_DIR / "campaigns.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Campaigns data not found: {file_path}")
    df = pd.read_csv(file_path)
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["spend"] = pd.to_numeric(df["spend"], errors="coerce")
    df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce")
    df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce")
    df["orders"] = pd.to_numeric(df["orders"], errors="coerce")
    df["roi"] = pd.to_numeric(df["roi"], errors="coerce")
    return df


def load_tasks(path: Path | str | None = None) -> pd.DataFrame:
    """Load merchant tasks CSV and return a DataFrame."""
    file_path = Path(path) if path else SAMPLE_DATA_DIR / "merchant_tasks.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Tasks data not found: {file_path}")
    return pd.read_csv(file_path)


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all three mock datasets at once."""
    return load_products(), load_campaigns(), load_tasks()
