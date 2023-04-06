"""
Semantic analyser for Nimble

Author: Greg Phillips

Version: 2023-03-28

"""
from nimble import NimbleListener, NimbleParser
from .errorlog import ErrorLog, Category
from .symboltable import PrimitiveType, FunctionType, Scope

TYPES = {'Int': PrimitiveType.Int,
         'Bool': PrimitiveType.Bool,
         'String': PrimitiveType.String}


class DefineScopesAndSymbols(NimbleListener):

    def __init__(self, error_log: ErrorLog, global_scope: Scope, types: dict):
        self.error_log = error_log
        self.current_scope = global_scope
        self.type_of = types

    def enterFuncDef(self, ctx: NimbleParser.FuncDefContext):
        func_name = ctx.ID().getText()
        return_type = PrimitiveType[ctx.TYPE().getText()] if ctx.TYPE() else PrimitiveType.Void
        if not self.current_scope.resolve_locally(func_name):
            parameter_types = [PrimitiveType[p.TYPE().getText()] for p in ctx.parameterDef()]
            self.current_scope.define(func_name, FunctionType(parameter_types, return_type))
        else:
            self.error_log.add(ctx, Category.DUPLICATE_NAME,
                               f'{func_name} already defined in {self.current_scope.name} scope')
        self.current_scope = self.current_scope.create_child_scope(func_name, return_type)

    def exitFuncDef(self, ctx: NimbleParser.FuncDefContext):
        self.current_scope = self.current_scope.enclosing_scope

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.create_child_scope('$main', PrimitiveType.Void)

    def exitMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.enclosing_scope


class InferTypesAndCheckConstraints(NimbleListener):
    """
    The type of each expression parse tree node is calculated and attached to the node as a
    `type` attribute, e.g,. self.type_of[ctx] = ...

    The types of declared variables are stored in `self.variables`, which is a dictionary
    mapping from variable names to symboltable.PrimitiveType instances.

    Any semantic errors detected, e.g., undefined variable names,
    type mismatches, etc, are logged in the `error_log`
    """

    def __init__(self, error_log: ErrorLog, global_scope: Scope, types: dict):
        self.error_log = error_log
        self.current_scope = global_scope
        self.type_of = types

    # --------------------------------------------------------
    # Program structure
    # --------------------------------------------------------

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.child_scope_named('$main')

    def exitMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.enclosing_scope

    def enterFuncDef(self, ctx: NimbleParser.FuncDefContext):
        self.current_scope = self.current_scope.child_scope_named(ctx.ID().getText())

    def exitFuncDef(self, ctx: NimbleParser.FuncDefContext):
        self.current_scope = self.current_scope.enclosing_scope

    def exitReturn(self, ctx: NimbleParser.ReturnContext):
        required_type = self.current_scope.return_type
        returned_type = self.type_of[ctx.expr()] if ctx.expr() else PrimitiveType.Void
        if required_type != returned_type:
            self.error_log.add(ctx, Category.INVALID_RETURN,
                               f'Required to return {required_type}, returns {returned_type}')

    # --------------------------------------------------------
    # Variable and parameter declarations
    # --------------------------------------------------------

    def log_invalid_assign(self, ctx, var_name):
        self.error_log.add(ctx, Category.ASSIGN_TO_WRONG_TYPE,
                           f"Can't assign {self.type_of[ctx.expr()]} expression to variable"
                           f"{var_name} of type {self.current_scope.resolve(var_name)}")

    def duplicate_name(self, ctx, name):
        already_declared = self.current_scope.resolve_locally(name)
        if already_declared:
            self.error_log.add(ctx, Category.DUPLICATE_NAME,
                               f"Can't redeclare {name}; already declared as {already_declared}")
            return True
        return False

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):
        var_name = ctx.ID().getText()
        if not self.duplicate_name(ctx, var_name):
            self.current_scope.define(var_name, TYPES[ctx.TYPE().getText()])
            if ctx.expr() and self.current_scope.resolve(var_name).type != self.type_of[ctx.expr()]:
                self.log_invalid_assign(ctx, var_name)

    def exitParameterDef(self, ctx: NimbleParser.ParameterDefContext):
        name = ctx.ID().getText()
        if not self.duplicate_name(ctx, name):
            _type = PrimitiveType[ctx.TYPE().getText()]
            self.current_scope.define(name, _type, is_param=True)

    # --------------------------------------------------------
    # Statements
    # --------------------------------------------------------

    def exitAssignment(self, ctx: NimbleParser.AssignmentContext):
        var_name = ctx.ID().getText()
        symbol = self.current_scope.resolve(var_name)
        if symbol:
            if symbol.type != self.type_of[ctx.expr()]:
                self.log_invalid_assign(ctx, var_name)
        else:
            self.error_log.add(ctx, Category.UNDEFINED_NAME,
                               f'Assignment target {var_name} not declared')

    def check_boolean_condition(self, ctx, kind):
        if self.type_of[ctx.expr()] != PrimitiveType.Bool:
            self.error_log.add(ctx, Category.CONDITION_NOT_BOOL,
                               f"{kind} condition {ctx.getText()} has type {self.type_of[ctx.expr()]} not Bool")

    def exitWhile(self, ctx: NimbleParser.WhileContext):
        self.check_boolean_condition(ctx, 'While')

    def exitIf(self, ctx: NimbleParser.IfContext):
        self.check_boolean_condition(ctx, 'If')

    def exitPrint(self, ctx: NimbleParser.PrintContext):
        if self.type_of[ctx.expr()] == PrimitiveType.ERROR:
            self.error_log.add(ctx, Category.UNPRINTABLE_EXPRESSION,
                               f"Can't print expression {ctx.getText()} as it has type ERROR")

    def exitFuncCallStmt(self, ctx: NimbleParser.FuncCallStmtContext):
        pass  # any semantic errors addressed in function call; doesn't have a type

    # --------------------------------------------------------
    # Function call
    # --------------------------------------------------------

    def exitFuncCall(self, ctx: NimbleParser.FuncCallContext):
        name = ctx.ID().getText()
        symbol = self.current_scope.resolve(name)
        if not symbol:
            self.error_log.add(ctx, Category.UNDEFINED_NAME,
                               f'no function named {name}')
            self.type_of[ctx] = PrimitiveType.ERROR
        elif not isinstance(symbol.type, FunctionType):
            self.error_log.add(ctx, Category.INVALID_CALL,
                               f'{name} is a variable, not a function')
            self.type_of[ctx] = PrimitiveType.ERROR
        else:
            param_types = [self.type_of[e] for e in ctx.expr()]
            if param_types != symbol.type.parameter_types:
                self.error_log.add(ctx, Category.INVALID_CALL,
                                   f'parameters of type {param_types} provided'
                                   f'when {symbol.type.parameter_types} required')
                self.type_of[ctx] = PrimitiveType.ERROR
            else:
                self.type_of[ctx] = symbol.type.return_type

    # --------------------------------------------------------
    # Expressions
    # --------------------------------------------------------

    def exitIntLiteral(self, ctx: NimbleParser.IntLiteralContext):
        self.type_of[ctx] = PrimitiveType.Int

    def exitNeg(self, ctx: NimbleParser.NegContext):
        if ctx.op.text == '-' and self.type_of[ctx.expr()] == PrimitiveType.Int:
            self.type_of[ctx] = PrimitiveType.Int
        elif ctx.op.text == '!' and self.type_of[ctx.expr()] == PrimitiveType.Bool:
            self.type_of[ctx] = PrimitiveType.Bool
        else:
            self.type_of[ctx] = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.INVALID_NEGATION,
                               f"Can't apply {ctx.op.text} to {self.type_of[ctx.expr()].name}")

    def exitParens(self, ctx: NimbleParser.ParensContext):
        self.type_of[ctx] = self.type_of[ctx.expr()]

    def binary_on_ints(self, ctx, result_type):
        if self.type_of[ctx.expr(0)] == PrimitiveType.Int and self.type_of[ctx.expr(1)] == PrimitiveType.Int:
            self.type_of[ctx] = result_type
        else:
            self.type_of[ctx] = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.INVALID_BINARY_OP,
                               f"Can't apply {ctx.op.text} to {self.type_of[ctx.expr(0)]}"
                               f"and {self.type_of[ctx.expr(1)]}")

    def exitMulDiv(self, ctx: NimbleParser.MulDivContext):
        self.binary_on_ints(ctx, PrimitiveType.Int)

    def exitAddSub(self, ctx: NimbleParser.AddSubContext):
        if (ctx.op.text == '+' and
                self.type_of[ctx.expr(0)] == PrimitiveType.String and
                self.type_of[ctx.expr(1)] == PrimitiveType.String):
            self.type_of[ctx] = PrimitiveType.String
        else:
            self.binary_on_ints(ctx, PrimitiveType.Int)

    def exitCompare(self, ctx: NimbleParser.CompareContext):
        self.binary_on_ints(ctx, PrimitiveType.Bool)

    def exitVariable(self, ctx: NimbleParser.VariableContext):
        name = ctx.getText()
        symbol = self.current_scope.resolve(name)
        if not symbol:
            self.type_of[ctx] = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.UNDEFINED_NAME,
                               f'Name {name} is not declared')
        elif isinstance(symbol.type, FunctionType):
            self.type_of[ctx] = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.FUNCTION_USED_AS_VARIABLE,
                               f'Function {name} cannot be used as variable')
        else:
            self.type_of[ctx] = symbol.type

    def exitStringLiteral(self, ctx: NimbleParser.StringLiteralContext):
        self.type_of[ctx] = PrimitiveType.String

    def exitBoolLiteral(self, ctx: NimbleParser.BoolLiteralContext):
        self.type_of[ctx] = PrimitiveType.Bool

    def exitFuncCallExpr(self, ctx: NimbleParser.FuncCallExprContext):
        self.type_of[ctx] = self.type_of[ctx.funcCall()]
