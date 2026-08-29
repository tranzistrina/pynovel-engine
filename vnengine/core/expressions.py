from __future__ import annotations
import ast
import operator as op
from typing import Any

BINOPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Mod: op.mod,
    ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge,
    ast.And: lambda a, b: a and b, ast.Or: lambda a, b: a or b,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}
UNOPS = {ast.Not: op.not_, ast.USub: op.neg, ast.UAdd: op.pos}

class ExpressionError(ValueError):
    pass

def evaluate(expression: str, variables: dict[str, Any]) -> Any:
    expression = expression.strip()
    try: node = ast.parse(expression, mode="eval").body
    except SyntaxError as exc: raise ExpressionError(f"Invalid expression: {expression}") from exc
    return _eval(node, variables)

def _eval(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, ast.Name): return env.get(node.id, False)
    if isinstance(node, ast.List): return [_eval(x, env) for x in node.elts]
    if isinstance(node, ast.Tuple): return tuple(_eval(x, env) for x in node.elts)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNOPS: return UNOPS[type(node.op)](_eval(node.operand, env))
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result = True
            for value in node.values:
                result = _eval(value, env)
                if not result: return result
            return result
        result = False
        for value in node.values:
            result = _eval(value, env)
            if result: return result
        return result
    if isinstance(node, ast.BinOp) and type(node.op) in BINOPS: return BINOPS[type(node.op)](_eval(node.left, env), _eval(node.right, env))
    if isinstance(node, ast.Compare):
        left = _eval(node.left, env)
        for oper, comparator in zip(node.ops, node.comparators):
            right = _eval(comparator, env); fn = BINOPS.get(type(oper))
            if fn is None or not fn(left, right): return False
            left = right
        return True
    raise ExpressionError(f"Unsupported expression: {ast.dump(node)}")
