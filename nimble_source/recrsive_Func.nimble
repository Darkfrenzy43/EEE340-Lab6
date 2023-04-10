func my_func(one : Int) -> Int {
    var x : String = "Hello"
    print second_func(x)
    print "\n"
    return one + 10
}

func second_func(str : String) -> String {
    var y : Int = 10
    print y + 10
    print "\n"
    return str + " World"
}

var x : Int = 20
print my_func(x)
print "\n"
print x