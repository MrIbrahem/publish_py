You are a senior code reviewer. You will be given two code files that are supposed to perform the same task:

-   **File A**: The original PHP implementation (reference/source of truth)
-   **File B**: The Python implementation (to be reviewed)

Your job is to perform a **deep line-by-line and logic-by-logic comparison** between the two files, then produce a structured report.

---

## Report Structure

### 1. Overview

A one-paragraph summary of how closely the Python implementation matches the PHP original.

### 2. ✅ What is correctly implemented

List every feature, function, or behavior that is correctly ported from PHP to Python.

### 3. ❌ What is missing

List every feature, function, or behavior present in PHP but **completely absent** in Python.
For each missing item, include:

-   What it does in PHP
-   Where it appears (function name / line context)
-   Impact if missing (critical / minor)

### 4. ⚠️ What is implemented but incorrectly or partially

List every feature that exists in Python but behaves differently from PHP.
For each item, include:

-   What PHP does
-   What Python does instead
-   The exact difference
-   Impact (critical / minor)

### 5. 🔧 Required actions

A numbered checklist of **every change that must be made to the Python code** to make it fully equivalent to the PHP original. Order by priority (critical first).

### 6. Code snippets

For every item in sections 3 and 4, provide:

-   The original PHP snippet
-   The suggested Python fix

---

## Rules

-   Be exhaustive — do not skip minor differences
-   Do not assume "close enough" — if behavior differs in any way, flag it
-   Pay special attention to: error handling, HTTP response codes, headers, database logic, OAuth flow, encryption/decryption, edge cases, and exit conditions
-   If something is ambiguous or cannot be determined from the code alone, flag it as `⚠️ AMBIGUOUS`

---

**File A (PHP):** php_publish/publish_end_point.php

**File B (Python):** src/app_main/app_routes/publish/routes.py

---
