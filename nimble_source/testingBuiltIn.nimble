
// Damn we've got a lot of these test cases we should probably organize them soon xD

func doStringStuff(in_str : String, start_ind : Int, str_len : Int) {

    var newStr : String = substring(in_str, start_ind, str_len)
    var strLen : Int = stringlength(in_str)

    print "\nOriginal string was: "
    print in_str
    print "\nLength of original string is: "
    print strLen
    print "\nNew substring is: "
    print newStr

}

var myString : String = "This is a string."
var a : Int = 2
var b : Int = 9

doStringStuff(myString, a, b)



