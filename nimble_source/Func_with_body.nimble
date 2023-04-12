// ----------------------
// expected output
// 10
// 40
// ----------------------

func my_func() -> Int{
var x : Int = 25
var y : Int = 15
return x + y
}

var x : Int = 10
var y : Int

y = my_func()

print x
print "\n"
print y