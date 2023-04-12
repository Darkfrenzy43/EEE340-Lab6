// ----------------------
// expected output
// 89
// ----------------------
func f() -> Int {

    var f : Int = 89

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

print f()