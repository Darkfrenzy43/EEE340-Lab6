// ----------------------
// expected output
//
// 1
// 2
// 3
// 4
// 5
// all done
// all done2
// ----------------------
var x : Int = 0
var y : Int = 8
while x<5{
    x = x + 1
    print "\n"
    print x
}
print "\nall done"

while y<5{
    print "\nI should not be printed"
}
print "\nall done2"