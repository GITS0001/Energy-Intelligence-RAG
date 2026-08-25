import os
import sys
import json
import duckdb

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

METRICS_DIR = os.path.join("data", "processed", "metrics")
ANALYTICAL_CSV = os.path.join("data", "processed", "tables", "analytical_dataset.csv")

_metrics_cache = {}

def load_metrics_cache():
    global _metrics_cache
    if not _metrics_cache and os.path.exists(METRICS_DIR):
        for file_name in os.listdir(METRICS_DIR):
            if file_name.endswith(".json"):
                key = file_name.replace(".json", "")
                file_path = os.path.join(METRICS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        _metrics_cache[key] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Error reading {file_name}: {e}")
    return _metrics_cache

def get_tabular_context(query: str) -> dict:
    """
    Two-Tier Hybrid Tabular Engine:
    - Tier 1: Fast lookup in precomputed JSON metrics (household, weather, consumption, seasonal, holiday, tariff, acorn).
    - Tier 2: Zero-copy DuckDB SQL queries against analytical_dataset.csv if custom aggregation is required.
    """
    query_lower = query.lower()
    metrics = load_metrics_cache()
    matched_contexts = []
    used_sources = []

    # -------------------------------------------------------------
    # TIER 1: PRECOMPUTED METRICS LOOKUP
    # -------------------------------------------------------------
    if any(kw in query_lower for kw in ["household", "tariff", "tou", "std", "acorn", "demographic", "cluster", "consumer"]):
        if "household_stats" in metrics:
            matched_contexts.append(f"Household Statistics: {json.dumps(metrics['household_stats'])}")
            used_sources.append("household_stats.json")
        if "tariff_stats" in metrics and any(kw in query_lower for kw in ["tariff", "tou", "std"]):
            matched_contexts.append(f"Tariff Performance: {json.dumps(metrics['tariff_stats'])}")
            used_sources.append("tariff_stats.json")
        if "acorn_stats" in metrics and "acorn" in query_lower:
            matched_contexts.append(f"ACORN Group Breakdown: {json.dumps(metrics['acorn_stats'])}")
            used_sources.append("acorn_stats.json")

    if any(kw in query_lower for kw in ["weather", "temperature", "humidity", "rain", "wind", "cloud", "sun", "cold", "hot", "climate"]):
        if "weather_stats" in metrics:
            matched_contexts.append(f"Weather & Atmospheric Statistics: {json.dumps(metrics['weather_stats'])}")
            used_sources.append("weather_stats.json")

    if any(kw in query_lower for kw in ["season", "winter", "summer", "spring", "autumn", "month"]):
        if "seasonal_stats" in metrics:
            matched_contexts.append(f"Seasonal Consumption Metrics: {json.dumps(metrics['seasonal_stats'])}")
            used_sources.append("seasonal_stats.json")

    if any(kw in query_lower for kw in ["holiday", "bank holiday", "christmas", "easter", "new year"]):
        if "holiday_stats" in metrics:
            matched_contexts.append(f"UK Bank Holiday Energy Dynamics: {json.dumps(metrics['holiday_stats'])}")
            used_sources.append("holiday_stats.json")

    if any(kw in query_lower for kw in ["consumption", "kwh", "electricity", "power", "peak", "usage", "average energy", "max energy", "median"]):
        if "consumption_stats" in metrics:
            matched_contexts.append(f"Citywide Consumption Metrics & Percentiles: {json.dumps(metrics['consumption_stats'])}")
            used_sources.append("consumption_stats.json")

    if matched_contexts:
        return {
            "source": f"Precomputed Metrics ({', '.join(used_sources)})",
            "context": "\n".join(matched_contexts),
            "query_type": "metric"
        }

    # -------------------------------------------------------------
    # TIER 2: DUCKDB ZERO-COPY AD-HOC QUERY
    # -------------------------------------------------------------
    try:
        conn = duckdb.connect(database=":memory:")
        # Execute zero-copy aggregation directly on analytical_dataset.csv
        sql = f"""
            SELECT 
                COUNT(*) as total_rows,
                ROUND(AVG(energy_sum), 3) as avg_daily_energy_kwh,
                ROUND(MAX(energy_sum), 3) as max_daily_energy_kwh,
                ROUND(AVG(temperatureMax), 2) as avg_max_temp_c
            FROM '{ANALYTICAL_CSV}'
        """
        res_df = conn.execute(sql).df()
        context_str = f"DuckDB Ad-hoc Summary: {res_df.to_dict(orient='records')[0]}"
        conn.close()

        return {
            "source": f"DuckDB Query on {ANALYTICAL_CSV}",
            "context": context_str,
            "query_type": "duckdb"
        }
    except Exception as e:
        return {
            "source": "Tabular Engine Error",
            "context": f"Could not query tabular data: {str(e)}",
            "query_type": "error"
        }

if __name__ == "__main__":
    print("=" * 60)
    print("📊 TESTING HYBRID TABULAR ENGINE (load_tables.py)")
    print("=" * 60)

    test_q = "What is the average energy consumption for ToU households vs Standard tariffs?"
    res = get_tabular_context(test_q)

    print(f"Query: '{test_q}'")
    print(f"Type:   {res['query_type']}")
    print(f"Source: {res['source']}")
    print(f"Context Snippet:\n{res['context'][:300]}...")
    print("=" * 60)
