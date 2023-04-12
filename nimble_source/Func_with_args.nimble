// ----------------------
// expected output
// 10
// hello
// 68
// 22
// 0
// 580
// 568
// ----------------------
func my_func(one : Int, two : String) {

    var n : Int = 58

    print one
    print "\n"
    print two
    print "\n"
    print n + one
    print "\n"

}


func second_func(inNum : Int, returnIt : Bool) -> Int {

    if returnIt {
        return inNum
    }
    else {
        return 0
    }

}

func third_func(returnIt : Bool) -> Bool {
    return returnIt
}

var x : Int = 10
var y : Int = 12

my_func(10, "hello")

print x + y

print "\n"
print second_func(580, false)
print "\n"
print second_func(580, true)
print "\n"
print second_func(second_func(568, true), third_func(true))