"""
Performs semantic analysis of a provided parse tree, returning the computed
global scope object for use in code generation.

Author: Greg Phillips
Version: 2023-03-15
"""

from antlr4 import ParseTreeWalker
from .errorlog import ErrorLog
from .nimblesemantics import InferTypesAndCheckConstraints, DefineScopesAndSymbols
from .symboltable import Scope


class NimbleSemanticErrors(Exception):

    def __init__(self, error_log):
        self.error_log = error_log

    def __repr__(self):
        return repr(self.error_log)


def do_semantic_analysis(tree):
    error_log = ErrorLog()
    global_scope = Scope('$global', None, None)
    node_types = {}

    scopes_and_symbols = DefineScopesAndSymbols(error_log, global_scope, node_types)
    walker = ParseTreeWalker()
    walker.walk(scopes_and_symbols, tree)
    types_and_constraints = InferTypesAndCheckConstraints(error_log, global_scope, node_types)
    walker.walk(types_and_constraints, tree)

    if error_log.total_entries():
        raise NimbleSemanticErrors(error_log)
    else:
        return global_scope, node_types
