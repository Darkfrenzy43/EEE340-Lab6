// ----------------------
// expected output
// Value of shadowed myVar in function: 100
//
// Value returned from function f(): 89
//
// Value of original myVar in main: 20
// ----------------------
func f() -> Int {

    var myVar : Int = 100   // shadowing a variable from main
    var f : Int = 89        // shadowing name of calling function

    print "\nValue of shadowed myVar in function: "
    print myVar

    if g(f) {
        return f
    }
    else {
        return 0
    }

}

func g(in_arg : Int) -> Bool {

    if in_arg < 100 {
        return true
    }
    else {
        return false
    }
}

var myVar : Int = 20    // Some variable declared in main
var returnedVal : Int = f()

print "\n\nValue returned from function f(): "
print returnedVal

print "\n\nValue of original myVar in main: "
print myVar