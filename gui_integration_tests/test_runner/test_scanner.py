import os, inspect, traceback, re, unittest
    
class TestScanner(object):

    def _get_package_path(self, package):
        """
        Returns the absolute path to this package.
        """
        mod = __import__(package, globals(), locals(), ['*'])
        return mod.__path__[0]

    def find_test_cases_for_package(self, package):
        test_case_class = unittest.TestCase
        root = self._get_package_path(package)
        modules_with_test_cases = []
        
        for path, dirs, files in os.walk(root, topdown=True):
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                f = open(os.path.join(path,file), 'r')
                import_pattern = re.compile('^\s*(import|from).*unittest')
                skip_pattern = re.compile('^.*#.*IGNORE_THIS_FILE')
                
                found_import = False
                for line in f:
                    if skip_pattern.match(line):
                        break
                    if import_pattern.match(line):
                        found_import = True
                        break
                    
                if not found_import: # No unittest import found in file.
                    continue
                
                module_name = self._get_module_name(package, root, path, file)
                
                try:
                    exec('import %s' % module_name)
                except Exception, val: 
                    print "ERROR: Could not import %s!" % module_name
                    
                    traceback.print_exc()
                    
                    continue

                module = eval(module_name)
                
                if inspect.ismodule(module):
                    members = inspect.getmembers(module)
                    
                    member_dict = {}
                    for key, value in members:
                        member_dict[key] = value
                    
                    for key in member_dict.keys():
                        try:
                            is_subclass = issubclass(
                                member_dict[key], 
                                test_case_class)
                        except: pass
                        else:
                            if is_subclass:
                                class_name = member_dict[key].__name__
                                
                                modules_with_test_cases.append(
                                    (module_name, class_name))
                        
                else:
                    print 'WARNING: %s is not a module!' % module
        
        print 'test scanner found...', modules_with_test_cases
        return modules_with_test_cases
        

    def _get_module_name(self, package, root, path, file):
        file = file[0:-len('.py')]
        
        path = path.replace(root, '')
        if path.startswith(os.sep):
            path = path[1:]
        module_path = path.replace(os.sep, '.')
        
        if module_path is not '':
            module_path = '.'.join([package, module_path])
        else:
            module_path = package
            
        return '.'.join([module_path, file])


import unittest

main_test_case = 'TestTestScanner'
class TestTestScanner(unittest.TestCase):
    
    def test_get_module_name(self):
        package = 'gui_integration_tests'
        base_path = os.path.join('workspace', 'flash_volunteer', package)
        module_name = 'test_scanner'
        file_name = '%s.py' % module_name
        path = TestScanner()._get_module_name(
            package,
            base_path,
            os.path.join(base_path, 'test_runner'),
            file_name)
        
        expected = '%s.test_runner.%s' % (package, module_name)
        self.assert_(path == expected,
            "Unexpected module path: Expected %s. Received %s."
                % (expected, path))
    
    def test_find_files_with_test_cases(self):
        package = 'gui_integration_tests'
        test_modules = TestScanner().find_test_cases_for_package(package)
        
        self.assert_(
            'gui_integration_tests.test_runner.test_scanner' in [i[0] for i in test_modules],
            "TestScanner did not find itself!")
            
        print test_modules
        for test_case in test_cases_in_this_file:
            self.assert_(
                test_case in [i[1] for i in test_modules],
                "TestScanner did not find one of its own test cases "
                "(%s)!" % test_case)
        
            
    def test_does_not_find_files_without_test_cases(self):
        scanner = TestScanner()
        package = 'gui_integration_tests'
        path = scanner._get_package_path(package)
        path = os.path.join(path, 'test_runner')
        
        module_name = 'test_scanner_test_file'
        file_name = '%s.py' % module_name
        file_name = os.path.join(path, file_name)
        
        f = open(file_name, 'w')
        
        f.write("""class TestClass(object):
    def test_method(self):
        print 'Delete me if you wish, for I am but a unit-test test file!'"""
            )
        
        f.close()
        
        self.assert_(os.path.exists(file_name))
        
        test_modules = scanner.find_test_cases_for_package(package)
                            
        self.assert_(
            '%s.test_runner.%s' % (package,module_name) not in test_modules,
            "TestScanner found a test file created without unit tests!")
        
        os.remove(file_name)
        

test_cases_in_this_file = [main_test_case]
for i in range(5):
    name = 'AutoTestCase%s' % i
    test_cases_in_this_file.append(name)
    exec("""class %s(unittest.TestCase):
    \"""Automatic test case generated for %s.\""" """ % (name, main_test_case))

    
if __name__ == '__main__':
    unittest.main()