"""
Templates used by the nimble2MIPS.py module

Authors: OCdt Brown & OCdt Velasco

Date: 01-04-2023
"""

script = """\
.data

true_string: .asciiz "true"
false_string: .asciiz "false"
    
{string_literals}

.text

true_false_string:
beq    $t0 $zero choose_false
la     $a0 true_string
j      end_true_false_string
choose_false:
la     $a0 false_string
end_true_false_string:
jr     $ra

main: 

move $fp $sp

{main}

halt:

li $v0 10
syscall
"""

add_sub_mul_div_compare = """\
{expr0}
addiu  $sp $sp -4 
sw     $t0 0($sp) 
{expr1}
lw     $s1 0($sp) 
{operation}    $t0 $s1 $t0 
addiu  $sp $sp 4
"""

while_ = """\
{startwhile_label}:
{condition}
beqz $t0 {endwhile_label}
{true_block}
b {startwhile_label}
{endwhile_label}:
"""

if_else_ = """\
{condition}
beqz   $t0 {endif_label}
{true_block}
b {endelse_label}
{endif_label}:
{false_block}
{endelse_label}:
"""

print_int_or_string = """\
{expr}
move   $a0 $t0
li     $v0 {service_code}
syscall
"""

# for printing booleans, we want to print true/false rather than 1/0
# so we start by loading the corresponding string address in to $a0
# using the true_false_string subroutine
#
# alternate approach: embed the true_false_subroutine code directly
# in the `print_bool` template, removing the `jr` instruction at the
# end and with unique, dynamically generated `choose_false` and
# `end_true_false_string` labels

print_bool = """\
{expr}
jal    true_false_string
li     $v0 4
syscall
"""

unary_minus = """\
{expr}
neg    $t0, $t0 
"""

# Consider looking at ixor
bool_neg = """\
{expr}
li     $s1 1
xor    $t0, $s1, $t0
"""

# Include assignment code here after
var_dec = """\
addiu  $sp $sp -4
{val_init}
sw     $t0 {offset}($fp)
"""

assigment = """\
{expr}
sw     $t0 {offset}($fp) 
"""

string_cat = """\

# Load registers with string addresses
{expr0}
sw $t0 0($sp)
addiu $sp $sp -4
{expr1}

# load expr1 into registers
move $s2 $t0
move $s6 $t0

# load expr0 into registers
lw $s0 4($sp)
lw $s5 4($sp)
addiu $sp $sp 4

# Count string chars
li $s1 0
{iter_char1}:
    lb $s4 0($s0)
    beqz $s4 {next_1}
    
    addiu $s1 1
    addiu $s0 1
    j {iter_char1}
{next_1}:

{iter_char2}:
    lb $s4 0($s2)
    beqz $s4 {fin_count}
    addiu $s1 1
    addiu $s2 1
    j {iter_char2}
{fin_count}:
    addiu $s1 1
    

# Allocate memory, store return address in $s0 and $s1
li $v0 9
move $a0 $s1
syscall
move $s0 $v0

# Copy the chars
{cp_chars_1}:
    lb $s4 0($s5)
    beqz $s4 {next_2}
    sb $s4 0($s0)
    addiu $s0 1
    addiu $s5 1
    j {cp_chars_1}
{next_2}:

{cp_chars_2}:
    lb $s4 0($s6)
    beqz $s4 {fin_cp}
    sb $s4 0($s0)
    addiu $s0 1
    addiu $s6 1
    j {cp_chars_2}
{fin_cp}:

    # Adding null term at end
    li $s4 0
    sb $s4 0($s0)
    
    # store result of expression in t0
    move $t0 $v0
"""
