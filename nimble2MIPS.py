"""
Given a global scope and type annotations, and operating as an ANTLR
listener over a semantically-correct Nimble parse tree, generates equivalent
MIPS assembly code. Does not consider function definitions, function calls,
or return statements.

Authors: OCdt Brown & OCdt Velasco          yeeee last lab of the course yeeee. lol goodluck finding this Brown.
Date: 01-04-2023                            im doing the cleaning, so odds are you won't see this lmaoooo.

Instructor version: 2023-03-15
"""

import templates
from nimble import NimbleListener, NimbleParser
from semantics import PrimitiveType


class MIPSGenerator(NimbleListener):

    def __init__(self, global_scope, types, mips):
        self.current_scope = global_scope
        self.types = types
        self.mips = mips
        self.label_index = -1
        self.string_literals = {}

    def unique_label(self, base):
        """
        Given a base string "whatever", returns a string of the form "whatever_x",
        where the x is a unique integer. Useful for generating unique labels.
        """
        self.label_index += 1
        return f'{base}_{self.label_index}'

    # ---------------------------------------------------------------------------------
    # Exit and Enter functions for lab 6
    # ---------------------------------------------------------------------------------

    def enterFuncDef(self, ctx: NimbleParser.FuncDefContext):
        # Switch scope to the calling function
        self.current_scope = self.current_scope.child_scope_named(ctx.ID().getText())

    def exitFuncDef(self, ctx: NimbleParser.FuncDefContext):
        # Extract function name
        func_name = ctx.ID().getText()

        # Set the MIPS translation.
        self.mips[ctx] = templates.enter_func_def.format(
            func_name=func_name,
            func_body=(self.mips[ctx.body()])
        )

        # Switch scope to enclosing scope
        self.current_scope = self.current_scope.enclosing_scope

    def exitReturn(self, ctx: NimbleParser.ReturnContext):
        # First handle if we're calling return in the main scope
        if self.current_scope.enclosing_scope.child_scope_named("$main") == self.current_scope:
            self.mips[ctx] = "li $v0 10\nsyscall"
        else:
            # If not in main, handle return accordingly if paired with expression
            self.mips[ctx] = templates.return_statment.format(
                expr=self.mips[ctx.expr()] if ctx.expr() is not None else ""
            )

    def exitFuncCall(self, ctx: NimbleParser.FuncCallContext):
        # Extract function argument expressions
        func_args = [this_expr for this_expr in ctx.expr()]

        # Construct script to push extracted arguments onto stack
        args_str = ""
        for arg in reversed(func_args):
            args_str += "addiu $sp $sp -4\n{}\nsw $t0 4($sp)\n".format(self.mips[arg])

        # Set translation
        self.mips[ctx] = templates.exit_func_call.format(
            func_name=ctx.ID().getText(),
            args_body=args_str,
            pop_args_offset=len(func_args) * 4    # <-- Field for popping arguments off stack at end
        )

    def exitFuncCallStmt(self, ctx: NimbleParser.FuncCallStmtContext):
        self.mips[ctx] = self.mips[ctx.funcCall()]

    def exitFuncCallExpr(self, ctx: NimbleParser.FuncCallExprContext):
        # If it exists, return statement will put return value in $t0
        self.mips[ctx] = self.mips[ctx.funcCall()]

    # ---------------------------------------------------------------------------------
    # Provided for you
    # ---------------------------------------------------------------------------------

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.child_scope_named('$main')

    def exitScript(self, ctx: NimbleParser.ScriptContext):
        # Extracting function definitions
        func_defs = "".join(self.mips[this_def] for this_def in ctx.funcDef())

        # Added stringlen and substring_template built-in function definitions
        self.mips[ctx] = templates.script.format(
            string_literals='\n'.join(f'{label}: .asciiz {string}' for label, string in self.string_literals.items()),
            main=self.mips[ctx.main()],
            func_defs=func_defs,
            stringlen=templates.stringlen,
            substring_template=templates.substring_template
        )

    def exitMain(self, ctx: NimbleParser.MainContext):
        self.mips[ctx] = self.mips[ctx.body()]
        self.current_scope = self.current_scope.enclosing_scope

    def exitBlock(self, ctx: NimbleParser.BlockContext):
        self.mips[ctx] = '\n'.join(self.mips[s] for s in ctx.statement())

    def exitBoolLiteral(self, ctx: NimbleParser.BoolLiteralContext):
        value = 1 if ctx.BOOL().getText() == 'true' else 0
        self.mips[ctx] = 'li     $t0 {}'.format(value)

    def exitIntLiteral(self, ctx: NimbleParser.IntLiteralContext):
        self.mips[ctx] = 'li     $t0 {}'.format(ctx.INT().getText())

    def exitStringLiteral(self, ctx: NimbleParser.StringLiteralContext):
        label = self.unique_label('string')
        self.string_literals[label] = ctx.getText()
        self.mips[ctx] = 'la     $t0 {}'.format(label)

    def exitPrint(self, ctx: NimbleParser.PrintContext):
        """
        Bool values have to be handled separately, because we print 'true' or 'false'
        but the values are encoded as 1 or 0
        """
        if self.types[ctx.expr()] == PrimitiveType.Bool:
            self.mips[ctx] = templates.print_bool.format(expr=self.mips[ctx.expr()])
        else:
            # in the SPIM print syscall, 1 is the service code for Int, 4 for String
            self.mips[ctx] = templates.print_int_or_string.format(
                expr=self.mips[ctx.expr()],
                service_code=1 if self.types[ctx.expr()] == PrimitiveType.Int else 4
            )

    # ---------------------------------------------------------------------------------
    # Partially provided for you - see lab instructions for suggested order
    # ---------------------------------------------------------------------------------

    def exitBody(self, ctx: NimbleParser.BodyContext):
        self.mips[ctx] = self.mips[ctx.varBlock()] + "\n" + self.mips[ctx.block()]

    def exitAddSub(self, ctx: NimbleParser.AddSubContext):
        """
        String concatenation and integer addition and subtraction are handled separately
        String concatenation is first. It is done by running the assembly code found in
        templates file. It is broken into two major parts. First the total length of each
        both strings is counted and stored in register $s1. In between the steps an area of
        memory is allocated of size $s1 and the pointer to the memory is stored in $s0
        The second step is to copy each of character from both of the strings into the newly
        allocated space including a null pointer at the end. The result is then stored in $t0

        add sub is much simpler. The nimble operation char is translated to the appropriate
        mips instruction. Each of the expressions is then the appropriate mips operation is
        applied on it with the result stored in $t0
        """

        if self.types[ctx.expr(0)] == PrimitiveType.String:
            self.mips[ctx] = templates.string_cat.format(
                expr0=self.mips[ctx.expr(0)],
                expr1=self.mips[ctx.expr(1)],
                iter_char1=self.unique_label('iter_char1'),
                iter_char2=self.unique_label('iter_char2'),
                next_1=self.unique_label('next_1'),
                fin_count=self.unique_label('fin_count'),
                cp_chars_1=self.unique_label('cp_chars_1'),
                next_2=self.unique_label('next_2'),
                cp_chars_2=self.unique_label('cp_chars_2'),
                fin_cp=self.unique_label('fin_cp')
            )
        else:
            self.mips[ctx] = templates.add_sub_mul_div_compare.format(
                operation='add' if ctx.op.text == '+' else 'sub',
                expr0=self.mips[ctx.expr(0)],
                expr1=self.mips[ctx.expr(1)]
            )

    def exitIf(self, ctx: NimbleParser.IfContext):
        self.mips[ctx] = templates.if_else_.format(
            condition=self.mips[ctx.expr()],
            true_block=self.mips[ctx.block(0)],
            endif_label=self.unique_label('endif'),
            false_block=self.mips[ctx.block(1)] if ctx.block(1) is not None else "",
            endelse_label=self.unique_label('endelse')  # Adding this is fine even when no else statement.
        )

    # ---------------------------------------------------------------------------------
    # Yours to implement - see lab instructions for suggested order
    # ---------------------------------------------------------------------------------

    def exitVarBlock(self, ctx: NimbleParser.VarBlockContext):
        self.mips[ctx] = '\n'.join(self.mips[s] for s in ctx.varDec())

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):
        # Reserve a slot in stack for declared local var
        slot_offset = (-4 * self.current_scope.resolve(ctx.ID().getText()).index)  # MODIFIED TO REMOVE EMPTY SPACE

        # Handle if there was assignment
        val_init_code = self.mips[ctx.expr()] if ctx.expr() is not None else (
            "li $t0 0" if PrimitiveType[ctx.TYPE().getText()] != PrimitiveType.ERROR else "")

        # Set the mips translation.
        self.mips[ctx] = templates.var_dec.format(
            val_init=val_init_code,
            offset=slot_offset
        )

    def exitAssignment(self, ctx: NimbleParser.AssignmentContext):
        # Get the symbol
        this_symbol = self.current_scope.resolve(ctx.ID().getText())

        # Needs to store the expression in the slot reserved for the variable
        # The slot reserved for the variable is found in the scope
        if this_symbol.is_param:
            slot_offset = (4 * (this_symbol.index + 1)) + 4
        else:
            slot_offset = -4 * this_symbol.index
        self.mips[ctx] = templates.assigment.format(
            expr=self.mips[ctx.expr()],
            offset=slot_offset
        )

    def exitWhile(self, ctx: NimbleParser.WhileContext):
        self.mips[ctx] = templates.while_.format(
            condition=self.mips[ctx.expr()],
            true_block=self.mips[ctx.block()],
            startwhile_label=self.unique_label("startwhile"),
            endwhile_label=self.unique_label("endwhile")
        )

    def exitNeg(self, ctx: NimbleParser.NegContext):
        # Unary minus code
        if ctx.op.text == '-':
            self.mips[ctx] = templates.unary_minus.format(expr=self.mips[ctx.expr()])
        # Boolean negation code
        elif ctx.op.text == '!':
            self.mips[ctx] = templates.bool_neg.format(expr=self.mips[ctx.expr()])

    def exitParens(self, ctx: NimbleParser.ParensContext):
        self.mips[ctx] = self.mips[ctx.expr()]

    def exitCompare(self, ctx: NimbleParser.CompareContext):
        self.mips[ctx] = templates.add_sub_mul_div_compare.format(
            operation='seq' if ctx.op.text == '==' else ('sle' if ctx.op.text == '<=' else 'slt'),
            expr0=self.mips[ctx.expr(0)],
            expr1=self.mips[ctx.expr(1)]
        )

    def exitVariable(self, ctx: NimbleParser.VariableContext):
        # Get the symbol
        this_symbol = self.current_scope.resolve(ctx.ID().getText())

        # Calculate offset accordingly if the accessed variable is or is not a parameter
        if this_symbol.is_param:
            var_offset = (4 * (this_symbol.index + 1)) + 4
        else:
            var_offset = (-4 * this_symbol.index)

        # Set the translation
        self.mips[ctx] = "lw   $t0  {}($fp)".format(var_offset)

    def exitMulDiv(self, ctx: NimbleParser.MulDivContext):
        self.mips[ctx] = templates.add_sub_mul_div_compare.format(
            operation='mul' if ctx.op.text == '*' else 'div',
            expr0=self.mips[ctx.expr(0)],
            expr1=self.mips[ctx.expr(1)]
        )
