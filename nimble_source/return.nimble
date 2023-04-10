

func testing_return() {

    print "\nThis should print."
    return
    print "\nThis should not print."

}


var x : Int = 12
print x


testing_return()

return

testing_return() // Shouldn't do anything. But it does! oh no

return
print "This should not be printed"

