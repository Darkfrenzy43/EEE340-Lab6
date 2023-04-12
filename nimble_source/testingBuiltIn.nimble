// --------------------------
//  Expected output:
//
//  Original string was: "This is a string. Here's a second part to the string. Aaaannd a third part too."
//  Length of input string is: 79
//  New substring is: "is is a string. Here's a s"
//
// --------------------------

func doStringStuff(in_str : String, start_ind : Int, str_len : Int) {

    // Declare vars
    var newStr : String
    var strLen : Int

    // Yeah let's amend this input string
    in_str = in_str + " Here's a second part to the string." + " Aaaannd a third part too."

    // Assign some values
    newStr = substring(in_str, start_ind, str_len)
    strLen = stringlength(in_str)

    print "\nOriginal string was: \""
    print in_str
    print "\"\nLength of input string is: "
    print strLen
    print "\nNew substring is: \"" + newStr + "\""

}

var myString : String = "This is a string."
var a : Int = 2
var b : Int = 26

doStringStuff(myString, a, b)



