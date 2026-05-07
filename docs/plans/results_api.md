You are a senior backend engineer specializing in PHP-to-Python migrations.

Your task is to analyze an existing PHP API implementation and create a detailed migration plan for a Python implementation that mirrors the PHP behavior exactly.

You will receive these files:

-   PHP source:

    -   `src/results_api_php`

-   Python source:
    -   `src/sqlalchemy_app/public/routes/main/routes.py`
    -   `src/sqlalchemy_app/public/routes/main/results_api.py`

The PHP code currently works and returns real results.
The Python code currently only parses query parameters and returns an empty result.

The PHP endpoint contains logic like:

```php
$camp  = $_GET['camp'] ?? "";
$depth = $_GET['depth'] ?? "1";
$code  = $_GET['code'] ?? "ar";
```

The Python code currently contains:

```python
code = request.args.get("code")
camp = request.args.get("camp")
depth = request.args.get("depth")

def results_api_result(code, camp, depth):
    result = {}
    return result
```

Your job:

1. Read and understand the PHP implementation completely.
2. Reverse-engineer the full request flow.
3. Identify:

    - validation logic
    - default values
    - SQL queries
    - filtering logic
    - recursion/depth handling
    - response structure
    - formatting rules
    - helper functions
    - hidden assumptions
    - edge cases

4. Analyze the Python structure and architecture.
5. Compare PHP responsibilities against the current Python implementation.
6. Produce a detailed migration plan explaining:

    - what is missing in Python
    - which PHP functions map to which Python functions
    - how to structure the Python implementation
    - what helper functions/classes are needed
    - how database access should work
    - how to preserve response compatibility

7. Do NOT rewrite the entire code immediately.
8. First produce:

    - architecture analysis
    - behavior mapping
    - implementation strategy
    - ordered task list

9. Include suggested Python function signatures.
10. Include notes about:

    - Flask/FastAPI routing compatibility
    - SQLAlchemy integration
    - serialization differences between PHP and Python
    - recursion/performance concerns
    - testing strategy for parity with PHP responses

11. If the PHP behavior is ambiguous, explicitly identify ambiguities and propose safe interpretations.
12. Output should be technical, structured, and migration-focused.

Format the response as:

# PHP Behavior Analysis

# Python Current State

# Missing Features

# Behavior Mapping (PHP → Python)

# Recommended Python Architecture

# Step-by-Step Migration Plan

# Edge Cases

# Testing Strategy

# Suggested Final Function Layout
