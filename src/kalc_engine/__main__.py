import sys
import os

# Support both module import and direct execution
if __package__:
    from .evaluator import Evaluator, EvalError
else:
    # Direct execution: add src directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from kalc_engine.evaluator import Evaluator, EvalError


def main() -> None:
    """Interactive REPL for calculator."""
    ev = Evaluator()
    mode = 'basic'
    print('KalcEngine — Multi-Mode Calculator')
    print('Type expressions to evaluate. Commands start with a dot: .help')
    print()
    while True:
        try:
            line = input(f'{mode}> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.startswith('.'):
            parts = line[1:].split()
            cmd = parts[0].lower()
            if cmd in ('exit', 'quit'):
                break
            if cmd == 'help':
                print()
                print('┌─────────────────────────────────────────────────────┐')
                print('│          KalcEngine — Command Reference             │')
                print('└─────────────────────────────────────────────────────┘')
                print()
                print('COMMANDS:')
                print('  ├─ .mode <basic|scientific|programmer>')
                print('  │  └─ Set evaluation mode')
                print('  ├─ .help')
                print('  │  └─ Show this help message')
                print('  └─ .exit / .quit')
                print('     └─ Exit the calculator')
                print()
                print('EXAMPLES:')
                print('  ├─ Basic Mode:')
                print('  │  ├─ 2 + 2')
                print('  │  └─ 10 * 5 - 3')
                print('  ├─ Scientific Mode:')
                print('  │  ├─ sin(3.14159/2)')
                print('  │  └─ 2 ^ 8  (power)')
                print('  └─ Programmer Mode:')
                print('     ├─ 0xFF & 0b1010  (hex & binary)')
                print('     └─ 15 << 2  (bitwise shift)')
                print()
                print('SUPPORTED FUNCTIONS:')
                print('  sin, cos, tan, asin, acos, atan, sqrt, abs')
                print('  log (base 10), ln (natural log), exp, floor, ceil')
                print()
                print('OPERATORS:')
                print('  Arithmetic: + - * / %')
                print('  Power: ^ or **')
                print('  Bitwise: & | ~ << >> (programmer mode)')
                print()
                continue
            if cmd == 'mode':
                if len(parts) >= 2 and parts[1] in ('basic', 'scientific', 'programmer'):
                    mode = parts[1]
                    print(f'mode -> {mode}')
                else:
                    print('Usage: .mode <basic|scientific|programmer>')
                continue
            print(f'Unknown command: {line} (type .help)')
            continue

        try:
            res = ev.evaluate(line, mode=mode)
            print(res)
        except EvalError as ee:
            print('Error:', ee)
        except Exception as e:
            print('Error:', e)


if __name__ == '__main__':
    main()
