# Python Idioms

Style patterns for Python execution.

---

## Paths

Use `pathlib.Path` for all path operations:
```python
from pathlib import Path
config_path = Path(__file__).parent / "config.json"
```

## Exceptions

Catch specific exceptions:
```python
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON: %s", e)
    raise
```

## Type Hints

Type hints for public interfaces:
```python
def process_signal(signal: dict[str, Any]) -> Spec:
    ...
```

## Testing

pytest conventions:
```python
def test_signal_extraction_handles_empty_input():
    result = extract_signal("")
    assert result["unclear"] == [{"item": "empty input", "options": []}]
```

## Logging

Use %-formatting for lazy evaluation:
```python
logger.debug("Processing %s with %d items", name, len(items))
```

## Context Managers

For resource cleanup:
```python
with open(path) as f:
    data = f.read()
```
