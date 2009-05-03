
from gui_integration_tests.test_runner.test_scanner import TestScanner

class PackageTestLoader(object):
    def load_tests_from_package(self, package, parent=__import__('__main__')):
        """
        Load test cases from the package with the given name
        into the parent object. Use __import__('__main__') as the parent if you 
        wish to simply run unittest.main. Otherwise, call 
        unittest.main(module=parent).
        """

        test_cases = TestScanner().find_test_cases_for_package(package)
        
        test_case_objects = []

        for module, test_case in test_cases:
            # Create a unique import name.
            import_name = '%s___%s' % (module, test_case)
            import_name = '__'.join(import_name.split('.'))
            exec('from %s import %s as %s' % (module, test_case, import_name))
            test_case_objects.append((import_name, eval(import_name)))
        
        for object_name, object in test_case_objects:
            parent.__dict__[object_name] = object