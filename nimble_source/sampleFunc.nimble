// ----------------------
// expected output
// This function doesn't have a return statement.
// 10
// ----------------------

// Just make it empty
func my_func() {
}

func just_print_no_return() {
    print "\nThis function doesn't have a return statement.\n"
}


var x : Int = 10

my_func()
just_print_no_return()

print x