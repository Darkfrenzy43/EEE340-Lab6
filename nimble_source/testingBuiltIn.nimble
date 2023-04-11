
// Damn we've got a lot of these test cases we should probably organize them soon xD

func doStringStuff(in_str : String, start_ind : Int, str_len : Int) {

    // Declare vars
    var newStr : String
    var strLen : Int

    // Yeah let's amend this input string
    in_str = in_str + " Here's a second part to the string."

    // Assign some values
    newStr = substring(in_str, start_ind, str_len)
    strLen = stringlength(in_str)

    print "\nOriginal string was: \""
    print in_str
    print "\"\nLength of input string is: "
    print strLen
    print "\nNew substring is: \""
    print newStr
    print "\""

}

var myString : String = "This is a string."
var a : Int = 2
var b : Int = 26

doStringStuff(myString, a, b)



