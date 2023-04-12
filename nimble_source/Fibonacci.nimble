// ----------------------
// expected output
// num =1   len =5
// num =2   len =4
// num =3   len =3
// num =5   len =2
// num =8   len =1
// ----------------------
func fibonacci(first : Int, second : Int, len : Int){
    if 0 < len {
    print "num ="
    print first + second
    print "\t"
    print "len ="
    print len
    print "\n"

    fibonacci(second, first+second, len-1)
    }
}

fibonacci(0, 1, 5) // fibonacii() doesn't return anything