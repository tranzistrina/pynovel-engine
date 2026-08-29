from __future__ import annotations
import ast
import operator as op
from typing import Any

BINOPS={ast.Add:op.add,ast.Sub:op.sub,ast.Mult:op.mul,ast.Div:op.truediv,ast.Mod:op.mod,ast.Eq:op.eq,ast.NotEq:op.ne,ast.Lt:op.lt,ast.LtE:op.le,ast.Gt:op.gt,ast.GtE:op.ge,ast.And:lambda a,b:a and b,ast.Or:lambda a,b:a or b}
UNOPS={ast.Not:op.not_,ast.USub:op.neg,ast.UAdd:op.pos}
class ExpressionError(ValueError): pass

def evaluate(expression:str,variables:dict[str,Any])->Any:
    try: node=ast.parse(expression,mode='eval').body
    except SyntaxError as exc: raise ExpressionError(expression) from exc
    return _eval(node,variables)

def _eval(node:ast.AST,env:dict[str,Any])->Any:
    if isinstance(node,ast.Constant): return node.value
    if isinstance(node,ast.Name): return env.get(node.id,False)
    if isinstance(node,ast.UnaryOp) and type(node.op) in UNOPS:return UNOPS[type(node.op)](_eval(node.operand,env))
    if isinstance(node,ast.BoolOp):
        vals=[_eval(v,env) for v in node.values]; return all(vals) if isinstance(node.op,ast.And) else any(vals)
    if isinstance(node,ast.BinOp) and type(node.op) in BINOPS:return BINOPS[type(node.op)](_eval(node.left,env),_eval(node.right,env))
    if isinstance(node,ast.Compare):
        left=_eval(node.left,env)
        for oper,comp in zip(node.ops,node.comparators):
            right=_eval(comp,env); fn=BINOPS.get(type(oper))
            if fn is None or not fn(left,right): return False
            left=right
        return True
    raise ExpressionError(f'Unsupported expression: {ast.dump(node)}')
