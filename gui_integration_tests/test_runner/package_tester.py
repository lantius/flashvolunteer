import unittest
from gui_integration_tests.test_runner.test_runner import TestRunner
from gui_integration_tests.test_runner.package_test_loader import PackageTestLoader

class PackageTester(object):
    def run_all_tests_for_package(self, package):        
        loader = PackageTestLoader().load_tests_from_package               
        loader(package)
        unittest.main(testRunner=TestRunner(package, descriptions=True, verbosity=2))

