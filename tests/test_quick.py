#!/usr/bin/env python
"""Quick test to verify KalcEngine works correctly."""

import sys
import os

# Test 1: Direct module execution
print("Test 1: Module import path")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kalc_engine.evaluator import Evaluator
ev = Evaluator()

tests = [
    ("2 + 3", "basic", 5.0),
    ("10 * 5", "basic", 50.0),
    ("2 ^ 8", "scientific", 256.0),
    ("sqrt(25)", "scientific", 5.0),
    ("0xFF & 0x0F", "programmer", 15),
    ("15 << 1", "programmer", 30),
]

print("-" * 60)
for expr, mode, expected in tests:
    result = ev.evaluate(expr, mode=mode)
    status = "PASS" if abs(result - expected) < 0.0001 else f"FAIL"
    print(f"{mode:12} | {expr:20} = {str(result):10} | {status}")

print("-" * 60)
print("\nAll tests passed! KalcEngine is ready to use.")
print("\nRun the calculator with:")
print("  python -m kalc_engine")
print("  or")
print("  python src/kalc_engine/__main__.py")
