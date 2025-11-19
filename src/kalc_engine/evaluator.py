import math
import re
from typing import List, Tuple, Union

Token = Tuple[str, str]  # (type, value)

class EvalError(Exception):
    pass
## nothing
class Evaluator:
    NUMBER_RE = re.compile(r"^0[bB][01]+|^0[oO][0-7]+|^0[xX][0-9a-fA-F]+|^\d*\.?\d+(?:[eE][+-]?\d+)?")
    IDENT_RE = re.compile(r"^[A-Za-z_]\w*")

    def __init__(self):
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': lambda x: math.log10(x),
            'ln': math.log,
            'exp': math.exp,
            'sqrt': math.sqrt,
            'abs': abs,
            'floor': math.floor,
            'ceil': math.ceil,
        }

        self.ops = {
            '+': (2, 'left'),
            '-': (2, 'left'),
            '*': (3, 'left'),
            '/': (3, 'left'),
            '%': (3, 'left'),
            '**': (5, 'right'),
            '^': (4, 'right'),  # interpreted per-mode: either pow or xor
            '&': (1, 'left'),
            '|': (1, 'left'),
            '~': (6, 'right'),  
            '<<': (1, 'left'),
            '>>': (1, 'left'),
        }

    def tokenize(self, expr: str) -> List[Token]:
        s = expr.replace(' ', '')  
        i = 0
        tokens: List[Token] = []
        while i < len(s):
            ch = s[i]
            # size>1 operators
            if s.startswith('**', i):
                tokens.append(('OP', '**'))
                i += 2
                continue
            if s.startswith('<<', i) or s.startswith('>>', i):
                tokens.append(('OP', s[i:i+2]))
                i += 2
                continue
            # ssize=1 ops
            if ch in '()+-*/%^~,&|<>':
                tokens.append(('OP', ch))
                i += 1
                continue
            # num
            m = self.NUMBER_RE.match(s[i:])
            if m:
                val = m.group(0)
                tokens.append(('NUMBER', val))
                i += len(val)
                continue
            # functions
            m = self.IDENT_RE.match(s[i:])
            if m:
                val = m.group(0)
                tokens.append(('IDENT', val))
                i += len(val)
                continue
            raise EvalError(f"Unknown token starting at: '{s[i:]}'")
        return tokens

    def _to_number(self, token: str, programmer: bool) -> Union[int, float]:
        # support prefixes for programmer/integer parsing
        if token.startswith(('0b', '0B')):
            return int(token, 2)
        if token.startswith(('0o', '0O')):
            return int(token, 8)
        if token.startswith(('0x', '0X')):
            return int(token, 16)
        # normal decimal or float
        if programmer and re.fullmatch(r"\d+", token):
            return int(token, 10)
        return float(token)

    def to_rpn(self, tokens: List[Token], mode: str) -> List[Token]:
        out: List[Token] = []
        stack: List[Token] = []

        def op_prec(op: str) -> int:
            return self.ops.get(op, (0, 'left'))[0]

        def assoc(op: str) -> str:
            return self.ops.get(op, (0, 'left'))[1]

        prev: Union[None, Token] = None
        for tok in tokens:
            ttype, val = tok
            if ttype == 'NUMBER':
                out.append(tok)
            elif ttype == 'IDENT':
                stack.append(tok)  # function or variable (only functions for now)
            elif ttype == 'OP':
                if val == ',':
                    # function arg separator (not used now)
                    while stack and stack[-1][1] != '(':
                        out.append(stack.pop())
                    if not stack:
                        raise EvalError('Mismatched parentheses or misplaced comma')
                elif val == '(':
                    stack.append(tok)
                elif val == ')':
                    while stack and stack[-1][1] != '(':
                        out.append(stack.pop())
                    if not stack:
                        raise EvalError('Mismatched parentheses')
                    stack.pop()  # pop '('
                    if stack and stack[-1][0] == 'IDENT':
                        out.append(stack.pop())  # function
                else:
                    # handle unary +, - and unary ~
                    if val in ('+', '-'):
                        # unary if previous token is None or previous is operator or '('
                        if prev is None or (prev[0] == 'OP' and prev[1] != ')'):
                            # convert to unary op representation
                            if val == '+':
                                val = 'u+'
                            else:
                                val = 'u-'
                    if val == '~':
                        # unary bitwise not
                        # keep as-is; evaluated as unary when in RPN
                        pass

                    # map '^' meaning depending on mode
                    if val == '^':
                        if mode == 'programmer':
                            op = '^'  # xor
                        else:
                            op = '**'  # treat caret as power in non-programmer
                    else:
                        op = val

                    if op not in self.ops and not op.startswith('u'):
                        # allow unary ops (u+, u-)
                        # allow other ops even if not in ops (they may be functions)
                        pass

                    # while there's an operator at top of stack with greater precedence
                    while stack and stack[-1][0] == 'OP':
                        top = stack[-1][1]
                        top_op = top
                        # handle ^ mapping for precedence comparison
                        if top_op == '^':
                            top_op = '**' if mode != 'programmer' else '^'
                        if top_op not in self.ops:
                            break
                        if (assoc(op) == 'left' and op_prec(top_op) >= op_prec(op)) or (
                            assoc(op) == 'right' and op_prec(top_op) > op_prec(op)
                        ):
                            out.append(stack.pop())
                        else:
                            break
                    stack.append(('OP', op))
            prev = tok
        while stack:
            t = stack.pop()
            if t[1] in ('(', ')'):
                raise EvalError('Mismatched parentheses')
            out.append(t)
        return out

    def eval_rpn(self, rpn: List[Token], mode: str) -> Union[int, float]:
        st: List[Union[int, float]] = []

        def to_int_if_needed(x):
            # in programmer mode, many ops should operate on ints
            if mode == 'programmer' and isinstance(x, float):
                if x.is_integer():
                    return int(x)
            return x

        for tok in rpn:
            ttype, val = tok
            if ttype == 'NUMBER':
                num = self._to_number(val, programmer=(mode == 'programmer'))
                st.append(num)
            elif ttype == 'IDENT':
                # function application
                if not st:
                    raise EvalError('Function missing argument')
                arg = st.pop()
                fn = self.functions.get(val.lower())
                if fn is None:
                    raise EvalError(f'Unknown function: {val}')
                res = fn(float(arg))
                st.append(res)
            elif ttype == 'OP':
                if val == 'u-':
                    a = st.pop()
                    st.append(-a)
                elif val == 'u+':
                    a = st.pop()
                    st.append(+a)
                elif val == '~':
                    a = st.pop()
                    a = to_int_if_needed(a)
                    if not isinstance(a, int):
                        raise EvalError('Bitwise operations require integer operands')
                    st.append(~a)
                elif val in ('+', '-', '*', '/', '%', '**'):
                    b = st.pop()
                    a = st.pop()
                    if val == '+':
                        st.append(a + b)
                    elif val == '-':
                        st.append(a - b)
                    elif val == '*':
                        st.append(a * b)
                    elif val == '/':
                        st.append(a / b)
                    elif val == '%':
                        st.append(a % b)
                    elif val == '**':
                        st.append(a ** b)
                elif val in ('&', '|', '^', '<<', '>>'):
                    b = st.pop()
                    a = st.pop()
                    a = to_int_if_needed(a)
                    b = to_int_if_needed(b)
                    if not isinstance(a, int) or not isinstance(b, int):
                        raise EvalError('Bitwise operations require integer operands')
                    if val == '&':
                        st.append(a & b)
                    elif val == '|':
                        st.append(a | b)
                    elif val == '^':
                        st.append(a ^ b)
                    elif val == '<<':
                        st.append(a << b)
                    elif val == '>>':
                        st.append(a >> b)
                else:
                    raise EvalError(f'Unsupported operator: {val}')
            else:
                raise EvalError(f'Unexpected token in RPN: {tok}')
        if len(st) != 1:
            raise EvalError('Malformed expression')
        return st[0]

    def evaluate(self, expr: str, mode: str = 'basic') -> Union[int, float]:
        """Evaluate expression string under given mode.

        mode: 'basic' | 'scientific' | 'programmer'
        Returns number (int for integer-like results in programmer mode when applicable, otherwise float).
        """
        if mode not in ('basic', 'scientific', 'programmer'):
            raise ValueError('Unknown mode')
        tokens = self.tokenize(expr)
        rpn = self.to_rpn(tokens, mode)
        res = self.eval_rpn(rpn, mode)
        # normalize programmer integer-like floats to int
        if mode == 'programmer' and isinstance(res, float) and res.is_integer():
            return int(res)
        return res


if __name__ == '__main__':
    ev = Evaluator()
    sample = ['2+2', '2**8', 'sin(3.14159/2)', '0xff & 0b1010', '5 ^ 2']
    for s in sample:
        print(s, '->', ev.evaluate(s, mode='scientific'))
