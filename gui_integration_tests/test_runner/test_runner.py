import time
import sys
from unittest import TestResult, _WritelnDecorator, _strclass
    
def hide_error_and_warning_words(message):
    words_to_hide = {
        'ERROR' : 'E R R O R',
        'Error' : 'E r r o r',
        'error' : 'e r r o r',
        'WARNING' : 'W A R N I N G',
        'Warning' : 'W a r n i n g',
        'warning' : 'w a r n i n g',
        'Fail' : 'F a i l',
        'fail' : 'f a i l',
    }
    for old, new in words_to_hide.iteritems():
        message = message.replace(old, new)
    return message

def _get_centered_string(input_string, width):
    if len(input_string) < width:
        diff = width - len(input_string)
        margin_len = int(diff/2)
        margin = ' ' * margin_len
        input_string = '%s%s' % (margin, input_string)
    return input_string
    
def get_test_method_name(test):   
    # str(test) returns the method name followed by a space then the class name in parens
    return str(test).split(' ')[0]
 
class _TestResult(TestResult):
    """A test result class that can print formatted text results to a stream.
    """
    sep_len = 80
    separator1 = '=' * sep_len
    separator2 = '-' * sep_len
    separator3 = '\xa6' * sep_len
    separator4 = '#' * sep_len
    separator5 = '\xa4' * sep_len
    
    ok_string = '%s( OK )%s' % ('-' * int((sep_len-6)/2), '-' * int((sep_len-6)/2))
    err_string = '%s( ERROR! )%s' % ('#' * int((sep_len-10)/2), '#' * int((sep_len-10)/2))
    fail_string = '%s( FAILURE! )%s' % ('#' * int((sep_len-12)/2), '#' * int((sep_len-12)/2))

    def __init__(self, stream, descriptions, verbosity):
        TestResult.__init__(self)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def startTest(self, test):
        TestResult.startTest(self, test)
        if self.showAll:
            self.stream.writeln()
            self.stream.writeln()
            self.stream.writeln(self.separator1)
            
            methodName = hide_error_and_warning_words(get_test_method_name(test))
            methodClass = hide_error_and_warning_words(_strclass(test.__class__))
            
            self.stream.writeln(_get_centered_string(methodClass, self.sep_len))
            self.stream.writeln(_get_centered_string(methodName, self.sep_len))
            
            self.stream.writeln(self.separator1)

    def addSuccess(self, test):
        TestResult.addSuccess(self, test)
        if self.showAll:
            self.stream.writeln(self.ok_string)
        elif self.dots:
            self.stream.write('.')

    def addError(self, test, err):
        TestResult.addError(self, test, err)
        if self.showAll:
            self.stream.writeln(self.errors[-1][1])
            self.stream.writeln(self.err_string)
        elif self.dots:
            self.stream.write('E')

    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        if self.showAll:
            self.stream.writeln(self.failures[-1][1])
            self.stream.writeln(self.fail_string)
        elif self.dots:
            self.stream.write('F')

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln()
            self.stream.writeln()
            self.stream.writeln(self.separator4)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator5)
            self.stream.writeln()
            self.stream.writeln("%s" % err)
            self.stream.writeln(self.separator5)

class TestRunner:
    """A test runner class that displays results in a nicely formatted textual 
    form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    def __init__(self, package, stream=sys.stderr, descriptions=False, verbosity=2):
        self.package = package
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity

    def _makeResult(self):
        return _TestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        
        self.stream.writeln()
        self.stream.writeln()
        
        if not result.wasSuccessful():
            self.stream.writeln(result.separator4)
        else:
            self.stream.writeln(result.separator3)
            
        self.stream.writeln()
        
        run = result.testsRun
        test_string = ("%d test%s (%.3fs)" 
            % (run, run != 1 and "s" or "", timeTaken))
        
        test_string = _get_centered_string(test_string, result.sep_len)

        package_name_msg = "'%s' package" % self.package
        self.stream.writeln(_get_centered_string(package_name_msg, result.sep_len))
        self.stream.writeln(test_string)
        
        self.stream.writeln()

        if not result.wasSuccessful():
            failed, errored = map(len, (result.failures, result.errors))
            status_string = "(failures=%d, errors=%d)" % (failed, errored)
            
            status_string = _get_centered_string(status_string, result.sep_len)
            
            self.stream.writeln(_get_centered_string('ERRORS!', result.sep_len))
            self.stream.writeln(status_string)
            
        else:
            self.stream.writeln(_get_centered_string("Everything seems fine", result.sep_len))
            
        self.stream.writeln()
        
        if not result.wasSuccessful():
            self.stream.writeln(result.separator4)
        else:
            self.stream.writeln(result.separator3)
            
        self.stream.writeln()
        return result
