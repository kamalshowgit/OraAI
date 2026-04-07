from agent.sql_agent import normalize_ai_identifiers
from main import build_error_payload


def test_normalize_ai_identifiers_quotes_schema_names():
    schema_map = {
        'dataset': [
            {'name': 'Entry Time', 'type': 'TEXT'},
            {'name': 'NET PnL', 'type': 'REAL'},
        ]
    }

    sql = 'CREATE TABLE daily_profit AS SELECT strftime("%Y-%m-%d", Entry_Time) AS Date, SUM(NET_PnL) AS Total_Daily_Profit FROM dataset GROUP BY strftime("%Y-%m-%d", Entry_Time)'
    normalized = normalize_ai_identifiers(sql, schema_map)

    assert '"Entry Time"' in normalized
    assert '"NET PnL"' in normalized
    assert 'Entry_Time' not in normalized


def test_build_error_payload_includes_generated_sql_and_suggestion():
    class DummyError(Exception):
        pass

    exc = DummyError("no such column: Entry_Time")
    payload = build_error_payload(exc, sql='SELECT Entry_Time FROM dataset')

    assert payload['message'] == 'no such column: Entry_Time'
    assert 'Entry_Time' in payload['suggestion']
    assert payload['generated_sql'] == 'SELECT Entry_Time FROM dataset'
