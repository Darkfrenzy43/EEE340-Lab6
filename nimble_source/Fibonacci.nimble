// ----------------------
// expected output
// num = 1
// num = 2
// num = 3
// num = 5
// num = 8
// num = 13
// num = 21
// num = 34
// num = 55
// num = 89
// ----------------------

// will generate the fibonacci sequence
func fibonacci(first : Int, second : Int, len : Int){
    if len == 0 {
        return
    }
    print "num = "
    print first + second
    print "\n"

    fibonacci(second, first+second, len-1)
}

fibonacci(0, 1, 10)