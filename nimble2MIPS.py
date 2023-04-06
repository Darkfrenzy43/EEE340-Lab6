"""
Given a global scope and type annotations, and operating as an ANTLR
listener over a semantically-correct Nimble parse tree, generates equivalent
MIPS assembly code. Does not consider function definitions, function calls,
or return statements.

Authors: TODO: Your names here
Date: TODO: Submission date here


STRING CONCAT:
    - need to generatere mips code to count number of bytes in string to null term
    - need generated code to copies bytes from source locatin to new buffer we created
    - we need to do this twice
    - to be clever, we can make it two mips subroutine in text section.
        Consider hand editing them to make life easier.

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
    # Provided for you
    # ---------------------------------------------------------------------------------

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.child_scope_named('$main')

    def exitScript(self, ctx: NimbleParser.ScriptContext):
        self.mips[ctx] = templates.script.format(
            string_literals='\n'.join(f'{label}: .asciiz {string}'
                                      for label, string in self.string_literals.items()),
            main=self.mips[ctx.main()]
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

        # TODO: extend for String concatenation
        if self.types[ctx.expr(0)] == PrimitiveType.String:
            iter_char1 = self.unique_label('iter_char1')
            iter_char2 = self.unique_label('iter_char2')
            next_1 = self.unique_label('next_1')
            next_2 = self.unique_label('next_2')
            fin_count = self.unique_label('fin_count')
            self.mips[ctx] = templates.string_cat.format(
                expr0=self.mips[ctx.expr(0)],
                expr1=self.mips[ctx.expr(1)],
                iter_char1=iter_char1,
                iter_char1_call=iter_char1,
                iter_char2=iter_char2,
                iter_char2_call=iter_char2,
                next_1=next_1,
                next_1_call=next_1,
                fin_count=fin_count,
                fin_count_call=fin_count,
            )
        else:
            self.mips[ctx] = templates.add_sub_mul_div_compare.format(
                operation='add' if ctx.op.text == '+' else 'sub',
                expr0=self.mips[ctx.expr(0)],
                expr1=self.mips[ctx.expr(1)]
            )

    def exitIf(self, ctx: NimbleParser.IfContext):

        # Is there a more efficient way to do this?
        false_block = "";
        if ctx.block(1) is not None:
            false_block = self.mips[ctx.block(1)];


        self.mips[ctx] = templates.if_else_.format(
            condition=self.mips[ctx.expr()],
            true_block=self.mips[ctx.block(0)],
            endif_label=self.unique_label('endif'),
            false_block = false_block,
            endelse_label=self.unique_label('endelse') # Yea adding this is fine even when no else statement.
        )


    # ---------------------------------------------------------------------------------
    # Yours to implement - see lab instructions for suggested order
    # ---------------------------------------------------------------------------------

    def exitVarBlock(self, ctx: NimbleParser.VarBlockContext):
        self.mips[ctx] = '\n'.join(self.mips[s] for s in ctx.varDec())

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):

        # Extract name and type
        var_name = ctx.ID().getText();
        var_type = PrimitiveType[ctx.TYPE().getText()];

        # Get the variables symbol and its index
        var_sym = self.current_scope.resolve(var_name);
        var_ind = var_sym.index;

        print("Var name is: {0}, type is {1}, index is {2}.".format(var_name, var_type, var_sym.index));

        # Reserve a slot in stack for declared local var
        slot_offset = -4 * (var_ind + 1);

        # If no expr added, initialize vars to their default value depending on type
        val_init_code = "";
        # Handle if there was assignment too
        if ctx.expr() is not None:
            val_init_code = self.mips[ctx.expr()]
        else:
            if var_type != PrimitiveType.ERROR:
                val_init_code = "li     $t0 0"

        # Set the mips translation. Test if works...
        self.mips[ctx] = templates.var_dec.format(
            val_init = val_init_code,
            offset = slot_offset
        )


    def exitAssignment(self, ctx: NimbleParser.AssignmentContext):
        # Needs to store the expression in the slot reserved for the variable
        # The slot reserved for the variable is found in the scope
        var_name = ctx.ID().getText()
        var_sym = self.current_scope.resolve(var_name)
        var_ind = var_sym.index
        slot_offset = -4 * (var_ind + 1)
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
            self.mips[ctx] = templates.unary_minus.format(expr = self.mips[ctx.expr()]);

        # Boolean negation code
        elif ctx.op.text == '!':
            self.mips[ctx] = templates.bool_neg.format(expr = self.mips[ctx.expr()]);

    def exitParens(self, ctx: NimbleParser.ParensContext):
        self.mips[ctx] = self.mips[ctx.expr()]

    def exitCompare(self, ctx: NimbleParser.CompareContext):
        self.mips[ctx] = templates.add_sub_mul_div_compare.format(
            operation='seq' if ctx.op.text == '==' else ('sle' if ctx.op.text == '<=' else 'slt'),
            expr0=self.mips[ctx.expr(0)],
            expr1=self.mips[ctx.expr(1)]
        )

    def exitVariable(self, ctx: NimbleParser.VariableContext):

        # Extract info on variable
        var_name = ctx.ID().getText()
        var_sym = self.current_scope.resolve(var_name);
        var_ind = var_sym.index;
        var_offset = -4 * (var_ind + 1);

        self.mips[ctx] = "lw   $t0  {}($fp)".format(var_offset);


    def exitMulDiv(self, ctx: NimbleParser.MulDivContext):

        self.mips[ctx] = templates.add_sub_mul_div_compare.format(
            operation = 'mul' if ctx.op.text == '*' else 'div',
            expr0 = self.mips[ctx.expr(0)],
            expr1 = self.mips[ctx.expr(1)]
        )


