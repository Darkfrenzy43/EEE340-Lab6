// ----------------------
// expected output
// 1
// after false if
// 0
// done
// ----------------------
var x : Int = 0
if true {
	print 1
}

print "\n"

if false {
	print 99  // shouldn't execute
}

print "after false if\n"

if x + 1 == 1 {
    print x
    print "\n"
}

print "done"
