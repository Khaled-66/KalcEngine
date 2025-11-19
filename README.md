# KalcEngine — Multi-mode Calculator

A lightweight, zero-dependency Python calculator with three powerful modes.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [File Hierarchy](#file-hierarchy)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Example Session](#example-session)
7. [How It Works](#how-it-works)
8. [Operator Precedence](#operator-precedence)
9. [Supported Functions](#supported-functions)
10. [Debugging & Extending](#debugging--extending)
11. [Testing](#testing)
12. [License](#license)

---

## Overview

KalcEngine evaluates mathematical expressions **safely** (no `eval()`). It supports three modes:

- **Basic**: arithmetic (+, -, \*, /, %)
- **Scientific**: functions and powers (sin, cos, tan, sqrt, log, ^ as power)
- **Programmer**: bitwise ops (&, |, ^, ~, <<, >>) and binary/hex/octal literals

---

## Features

- Pure Python (no external dependencies)
- Interactive CLI REPL with mode switching
- Correct operator precedence and associativity
- Safe parsing using **Tokenizer → Shunting Yard → RPN evaluation**
- Support for 11+ mathematical functions
- Unary operators (+, -, bitwise NOT ~)

---

## File Hierarchy

```
d:/KalcEngine/
│
├── src/
│   └── kalc_engine/                    # Main Python package
│       ├── __init__.py                 # Package initialization
│       ├── __main__.py                 # Entry point (CLI REPL)
│       │   └── main()                  # Interactive loop
│       │
│       └── evaluator.py                # Core calculation engine (~290 lines)
│           ├── Tokenizer               # Converts string → tokens
│           │   └── tokenize()          # Breaks expression into tokens
│           │
│           ├── Shunting Yard Parser    # Converts infix → postfix (RPN)
│           │   └── to_rpn()            # Handles precedence & associativity
│           │
│           └── RPN Evaluator           # Evaluates postfix expressions
│               ├── eval_rpn()          # Stack-based evaluation
│               ├── functions{}         # sin, cos, sqrt, etc.
│               └── ops{}               # Operator definitions
│
├── tests/
│   ├── test_evaluator.py               # Unit tests (pytest)
│   ├── test_quick.py                   # Quick verification script
│   └── test_input.txt                  # Test input data
│
├── setup.py                            # Package configuration & installation
├── README.md                           # This file
└── .git/                               # Version control
```

### Key Files Explained

| File                           | Purpose                               | Lines |
| ------------------------------ | ------------------------------------- | ----- |
| `src/kalc_engine/evaluator.py` | Core tokenizer, parser, evaluator     | ~290  |
| `src/kalc_engine/__main__.py`  | CLI REPL interface                    | ~80   |
| `tests/test_evaluator.py`      | Unit tests                            | ~30   |
| `tests/test_quick.py`          | Quick verification script             | ~20   |
| `tests/test_input.txt`         | Test input data                       | N/A   |
| `setup.py`                     | Package config (makes it installable) | ~20   |

---

## Installation

### Option 1: Install in Development Mode (Recommended)

```powershell
cd d:\KalcEngine
python -m pip install -e .
```

This makes the package available globally and allows edits to take effect immediately.

### Option 2: Run Without Installation

```powershell
cd d:\KalcEngine
python -m kalc_engine
```

Or directly:

```powershell
python src/kalc_engine/__main__.py
```

---

## Quick Start

### Running the Calculator

```powershell
python -m kalc_engine
```

### Commands in the REPL

- `.mode <basic|scientific|programmer>` — switch evaluation mode
- `.help` — show help and examples
- `.exit` or `.quit` — exit the calculator
- `Ctrl+C` or `Ctrl+D` — also exits

---

## Example Session

```
KalcEngine — Multi-Mode Calculator
Type expressions to evaluate. Commands start with a dot: .help

basic> 2 + 2
4.0
basic> .mode scientific
mode -> scientific
scientific> sin(3.14159/2)
0.9999999999991198
scientific> 2 ^ 8
256.0
scientific> .mode programmer
mode -> programmer
programmer> 0xFF & 0x0F
15
programmer> 15 << 2
60
programmer> .exit
```

---

## How It Works

### The Three-Phase Pipeline

KalcEngine processes expressions using:

```
USER INPUT
    ↓
[Phase 1] TOKENIZER        "2 + 3 * 4" → [2, +, 3, *, 4]
    ↓
[Phase 2] SHUNTING YARD    [2, +, 3, *, 4] → [2, 3, 4, *, +]  (RPN)
    ↓
[Phase 3] RPN EVALUATOR    [2, 3, 4, *, +] → 14.0
    ↓
RESULT
```

### Phase 1: Tokenization

Breaks input string into recognized tokens:

```
Input:    "2 + 3 * 4"
Tokens:   [('NUMBER','2'), ('OP','+'), ('NUMBER','3'), ('OP','*'), ('NUMBER','4')]
```

**Token Types:**

- `NUMBER`: `2`, `3.14`, `0xFF`, `0b1010`
- `IDENT`: `sin`, `cos`, `sqrt`
- `OP`: `+`, `-`, `*`, `/`, `^`, `**`, `&`, `|`, `<<`, `>>`
- `PAREN`: `(`, `)`

### Phase 2: Shunting Yard Parser

Converts infix notation (what humans write) to postfix notation (RPN — easy to evaluate).

**Why?** Because `3 * 4` should be evaluated before `2 +`, and the algorithm handles this automatically.

```
Input (Infix):   2 + 3 * 4
Output (RPN):    2 3 4 * +

Reading left-to-right:
  1. '2' → push to output
  2. '+' → push to operator stack
  3. '3' → push to output
  4. '*' (higher precedence than +) → push to operator stack
  5. '4' → push to output
  6. End: pop all operators → output

Result: [2, 3, 4, *, +]
```

### Phase 3: RPN Evaluation

Uses a stack to compute the result:

```
RPN: [2, 3, 4, *, +]

Step 1:  Push 2           Stack: [2]
Step 2:  Push 3           Stack: [2, 3]
Step 3:  Push 4           Stack: [2, 3, 4]
Step 4:  See *: pop 4,3 → 3*4=12, push 12  Stack: [2, 12]
Step 5:  See +: pop 12,2 → 2+12=14, push 14  Stack: [14]

Result: 14
```

---

## Operator Precedence

**Higher number = evaluated first**

| Operator     | Precedence | Associativity | Example             |
| ------------ | ---------- | ------------- | ------------------- |
| +, -         | 2          | left          | `2 - 1 - 1 = 0`     |
| \*, /, %     | 3          | left          | `10 * 2 / 4 = 5`    |
| ^ (power)    | 4          | right         | `2 ^ 3 ^ 2 = 512`   |
| \*\* (power) | 5          | right         | `2 ** 3 ** 2 = 512` |
| &, \|        | 1          | left          | bitwise AND/OR      |

**Associativity:**

- **Left**: `a ⊕ b ⊕ c = (a ⊕ b) ⊕ c`
  - Example: `10 - 5 - 2 = (10 - 5) - 2 = 3`
- **Right**: `a ⊕ b ⊕ c = a ⊕ (b ⊕ c)`
  - Example: `2 ** 3 ** 2 = 2 ** (3 ** 2) = 512`

---

## Supported Functions

| Function               | Mode       | Example                |
| ---------------------- | ---------- | ---------------------- |
| `sin`, `cos`, `tan`    | Scientific | `sin(3.14159/2)`       |
| `asin`, `acos`, `atan` | Scientific | `asin(1)`              |
| `log`                  | Scientific | `log(100)` (base 10)   |
| `ln`                   | Scientific | `ln(10)` (natural log) |
| `exp`                  | Scientific | `exp(1)` (e^x)         |
| `sqrt`                 | Scientific | `sqrt(16)`             |
| `abs`                  | Scientific | `abs(-5)`              |
| `floor`                | Scientific | `floor(3.7)`           |
| `ceil`                 | Scientific | `ceil(3.2)`            |

---

## Debugging & Extending

### Inspect Intermediate Steps

```python
from kalc_engine.evaluator import Evaluator

ev = Evaluator()

# See tokens
tokens = ev.tokenize("2 + 3 * 4")
print("Tokens:", tokens)

# See RPN
rpn = ev.to_rpn(tokens, mode="basic")
print("RPN:", rpn)

# See result
result = ev.eval_rpn(rpn, mode="basic")
print("Result:", result)
```

### Add a New Function

Edit `src/kalc_engine/evaluator.py`, find `self.functions = {...}`, and add:

```python
self.functions = {
    # ... existing ...
    'hypot': math.hypot,  # New function
}
```

Then test:

```python
ev.evaluate("hypot(3, 4)", mode="scientific")  # Returns 5.0
```

### Add a New Operator

1. Update `self.ops` dictionary with precedence
2. Update tokenizer to recognize it
3. Add handling in `eval_rpn()`

---

## Testing

### Quick Test

```powershell
python test_quick.py
```

### Unit Tests (requires pytest)

```powershell
pip install pytest
pytest tests/
```

### Example Tests

```python
from kalc_engine.evaluator import Evaluator

ev = Evaluator()

# Basic
assert ev.evaluate("2 + 2", mode="basic") == 4.0

# Scientific
assert abs(ev.evaluate("sin(0)", mode="scientific") - 0.0) < 0.0001

# Programmer
assert ev.evaluate("0xFF & 0x0F", mode="programmer") == 15
```

---

## License

Open source — free to use, modify, and distribute.

---

**Created:** November 2025  
**Repository:** https://github.com/Khaled-66/KalcEngine  
**Status:** Fully functional and ready to use
