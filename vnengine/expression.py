from __future__ import annotations

import ast
import operator
from collections.abc import Mapping
from typing import Any


class ExpressionError(ValueError):
    pass


class ExpressionEvaluator:
    """Small sandboxed expression evaluator for declarative game logic."""

    _binary_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    }
    _compare_ops = {
        ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Gt: operator.gt,
        ast.GtE: operator.ge, ast.Lt: operator.lt, ast.LtE: operator.le,
        ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
    }
    _bool_ops = {ast.And: all, ast.Or: any}

    def __init__(self, variables: Mapping[str, Any] | None = None):
        self.variables = variables if variables is not None else {}

    def evaluate(self, expression: str | bool | int | float | None) -> Any:
        if expression is None or isinstance(expression, (bool, int, float)):
            return expression
        if not isinstance(expression, str):
            raise ExpressionError("Expression must be a scalar or string")
        source = expression.strip()
        if not source:
            return True
        try:
            tree = ast.parse(source, mode="eval")
            return self._eval(tree.body)
        except ExpressionError:
            raise
        except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as exc:
            raise ExpressionError(f"Invalid expression: {source}") from exc

    def _eval(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if node.value is None or isinstance(node.value, (str, int, float, bool)):
                return node.value
            raise ExpressionError("Unsupported constant")
        if isinstance(node, ast.Name):
            return self.variables.get(node.id)
        if isinstance(node, ast.List): return [self._eval(x) for x in node.elts]
        if isinstance(node, ast.Tuple): return tuple(self._eval(x) for x in node.elts)
        if isinstance(node, ast.Dict): return {self._eval(k): self._eval(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand)
            if isinstance(node.op, ast.Not): return not bool(value)
            if isinstance(node.op, ast.USub): return -value
            if isinstance(node.op, ast.UAdd): return +value
            raise ExpressionError("Unsupported unary operator")
        if isinstance(node, ast.BinOp):
            func = self._binary_ops.get(type(node.op))
            if func is None: raise ExpressionError("Unsupported binary operator")
            return func(self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.BoolOp):
            values = [bool(self._eval(v)) for v in node.values]
            func = self._bool_ops.get(type(node.op))
            if func is None: raise ExpressionError("Unsupported boolean operator")
            return func(values)
        if isinstance(node, ast.Compare):
            left = self._eval(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval(comparator); func = self._compare_ops.get(type(op))
                if func is None: raise ExpressionError("Unsupported comparison operator")
                try: result = func(left, right)
                except TypeError as exc: raise ExpressionError("Incompatible comparison") from exc
                if not result: return False
                left = right
            return True
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name): raise ExpressionError("Only named helper calls are allowed")
            name = node.func.id
            if node.keywords: raise ExpressionError("Keyword arguments are not allowed")
            args = [self._eval(arg) for arg in node.args]
            if name == "has": return args and args[0] in self.variables
            if name == "has_item":
                items = self.variables.get("items", [])
                return bool(args) and args[0] in items
            if name == "truthy": return bool(args and args[0])
            raise ExpressionError(f"Unknown helper: {name}")
        raise ExpressionError(f"Unsupported expression node: {type(node).__name__}")
