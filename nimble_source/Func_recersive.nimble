func my_func(x : Int){
    var y : Int = x - 1
    if x == 0 {
        return
    } else {
        my_func(y)
        print y
    }
}

my_func(10)