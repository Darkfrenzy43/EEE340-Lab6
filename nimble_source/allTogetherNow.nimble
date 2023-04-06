// All together now! Time to test everything out in this nimble file

// --------------------- Expected output ---------------------
// Boolean value is: false
// theNumber is positive. Put a negative on it.
// Boolean value is: true
// theNumber is negative. You may proceed.
//
// 20 + 5 = 25
// (2 + 12) / 7 = 2
// ((9 * 9) / 9) - 9 = 0
//
//
// Here's a secret message... don't worry. It's appropriate:
// [insert secret URL here. Can't show it here because it's a secret]
// -----------------------------------------------------------



// Defining the variables
var theLink : String = ""
var theNumber : Int = 5
var theBoolean : Bool


// --- Main entry point ---

// Here's an unnecessarily complex while loop...

theBoolean = false
while !(theNumber < 0) {

    print "\nBoolean value is: "
    print theBoolean

    if theBoolean {
        theNumber = -(theNumber)
    }

    if theNumber < 0 {
        print "\ntheNumber is negative. You may proceed."
    }
    else {
        print "\ntheNumber is positive. Put a negative on it."
        theBoolean = true
    }
}

// A bit of arithmetic...
print "\n\n20 + 5 = "
print (20 + 5)
print "\n(2 + 12) / 7 = "
print (2 + 12) / 7
print "\n((9 * 9) / 9) - 9 = "
print ((9 * 9) / 9) - 9
print "\n\n"

// And a bit of (unnecessarily complex) string concatenation
while theNumber < 0 {

    if theNumber == -5 {
        theLink = theLink + "https://ww"
    }
    if theNumber == -4 {
        theLink = theLink + "w.yout"
    }
    if theNumber == -3 {
        theLink = theLink + "ube.co"
    }
    if theNumber == -2 {
        theLink = theLink + "m/watch?v="
    }
    if theNumber == -1 {
        theLink = theLink + "E4WlUXrJgy4"
    }

    // Increment theNumber
    theNumber = theNumber + 1
}

print "\n\nHere's a very important video... don't worry. It's appropriate: \n"
print theLink




