// ----------------------
// expected output
// str1str2str3
// str1str2str3newString
// hi hi
// hi hi hi
// hi hi hi hi
// hi hi hi hi hi
// hi hi hi hi hi hi
// HelloWorld!
// newline test
// str1str2str3str4
// str1 str2 str3 str4
// ----------------------
var x : String = "str1" + "str2" + "str3"
var y : String = x + "newString"
var z : String = "hi"
var i : Int = 0
var h : String
print x
print "\n"

print y
print "\n"

while i<5{
    z = z + " hi"
    print z
    print "\n"
    i = i + 1
}

h = "Hello" + "World!" + "\n"
print h
print "newline test"

print "\n" + x + "str4"

print "\n"
print ("str1 " + "str2 ") + ("str3 " + "str4 ")