func my_func(x : Int){
    var y : Int = x - 1
    if x == 0 {
        return
    } else {
        my_func(y)
        printer_func(y)
    }
}

func printer_func(x : Int) {
    var y : Int = add_10(x)
    print "\n"
    print y
}

func add_10(x : Int) -> Int {
    return x + 10
}

var outside : String = "\nOutside string after recursive function lmao."

my_func(10)

print outside