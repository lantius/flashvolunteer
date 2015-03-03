# Introduction #

Here are some notes on how to implement unit tests with GAEUnit, through experience and reading the sample code included in the GAEUnit project: http://code.google.com/p/gaeunit/

# Details #

Tests go in the /test folder, and are automatically executed when you visit the /test url.  Tests extend unittest.TestCase, and are metaprogrammed - there are a few reserved method definitions (setUp) but otherwise you simply define methods that will be called representing each test.  If the method returns successfully then it is counted as a pass, if it throws an exception then it is a failure but the remainder of the tests will run and the failure will be noted.  There are a few assertions to help out - assertEquals, assertTrue, etc.