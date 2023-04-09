
func my_func(one : Int, two : String) {

    var n : Int = 69

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
print second_func(420, false)
print "\n"
print second_func(420, true)
print "\n"
print second_func(second_func(568, true), third_func(true))