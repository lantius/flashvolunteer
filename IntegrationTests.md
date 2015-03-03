Use [Selenium](http://seleniumhq.org/) for writing/running automated GUI tests. Selenium allows for GUI test case construction through programming by demonstration. Initial Selenium tests can be authored in Firefox through a [plugin](http://seleniumhq.org/projects/ide/). There is also [support](http://seleniumhq.org/projects/remote-control/) for running the test cases on other browsers. Selenium also has a [distributed service](http://selenium-grid.seleniumhq.org/) for running your test suite on a variety of platforms/servers over EC2; this doesn't appear to be free.

Selenium test cases can be saved in a variety of formats, e.g. HTML. We will save them out as Python to be incorporated into unit tests. This will allow us to create a test framework for GUI tests that goes beyond the capabilities of Selenium, as described next.

## The GUI Integration Test Framework ##

The goal is to be able to test the gui in a way that it is easy to run the GUI tests (and so its inexcusable not to!) during dev, while also being able to quickly make new unit tests. In order to do this, I've implemented a test framework. It has the following features:
  1. all in python. the Selenium IDE can be used to produce python code, which can then be added as a test case.
  1. easily recreate sessions for use in multiple unit tests (so that every test doesn't need code to, say, create a user, login, and signout). TestCase classes can inherit from a number of TestCases with preconfigured setup/teardown protocols (like LogIn\_Volunteer). See gui\_integration\_tests.test\_cases
  1. populate an FV testing environment with various Volunteers, Events, Neighborhoods, etc for use in all/any tests. This is enabled by using google app engine's remote api so that the datastore can be directly manipulated. See gui\_integration\_tests.datastore\_interface.
  1. easily execute all unit tests. a test runner finds, runs, and formats the results of all unit tests in the framework. See gui\_integration\_tests.test\_runner.

The GUI integration test framework can be found in the repo under the gui\_integration\_tests directory. It is organized as follows:

gui\_integration\_tests /
  * navigation   :   tests related to basic navigation
  * page\_stressing  :  tests organized by page for in detail
  * task\_specific  :  tests regarding common tasks
  * test\_runner  :   contains modules to run/execute/format output from all unit tests found in the gui test framework
  * all\_tests.py  :  run this module to execute all GUI unit tests (using the test\_runner; follow the directions below to make sure you are in a position to run it)
  * datastore\_interface.py  :   Uses the remote\_api to work within the google app engine environment. Used to populate/depopulate the datastore and other queries for use in tests.
  * test\_settings.py  :  some settings that may be needed to be modified locally in order to get the testing to work
  * test\_cases.py   :   a set of base unit TestCases that reconstruct certain contexts, populate an FV environment, etc, so that each test does not have to do it individually

## How to run the unit tests ##

Software prereqs:
  1. Install the Selenium python package (its available on pypi, so you can just do "easy\_install selenium")
  1. Download the [Selenium server](http://seleniumhq.org/projects/remote-control/)

To run the unit tests:
  1. You need to have Selenium Remote Server running (i.e. java -jar selenium-server.jar)
  1. You need to have the FV website running locally
  1. You need to make sure that gui\_integration\_tests.test\_settings accurately reflect your setup (in particular, the host and PYTHON\_LIB setting)

Now just run python on gui\_integration\_tests.all\_tests. Alternatively, you can run each test individually like any unit test.

## How to create unit tests ##

After installing the firefox Selenium plugin, open the IDE from the tools menu. See the documentation or the video for a description of creating the test case. After you've demonstrated a script, you can go to the source tab, which defaults to displaying an html file. This can be saved and loaded later, though often it assumes that some kind of session state exists. You can also swich the source format through the options menu, notably to python. Note that a generated python script won't work directly -- you need to integrate it into the GUI testing framework.

The best way to see how to integrate the Selenium produced code is just by reading a couple of the existing unit tests. A good place to start is gui\_integration\_framework.navigation.vol\_hit\_all\_nav. It is a unit test that simply clicks through the top navigation menus. The body of the test (test\_new) is a subset of the code that might be produced were you to record it in Selenium. Instead, it gets some initial state by inheriting from LoginFirst\_Volunteer. This parent class will login as a user/volunteer "volunteer0@test.org". This user was created, in turn, by BaseTestCase (the parent of LoginFirst\_Volunteer). That class can populate a FV environment with Volunteers, Events, etc (though it only creates Volunteers currently). In the test teardown, these objects are deleted. These base classes are useful for recreating the proper context for a wide set of unit tests.