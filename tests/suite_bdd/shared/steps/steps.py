# -*- coding: utf-8 -*-

# A quick introduction to implementing scripts for BDD tests:
#
# This file contains snippets of script code to be executed as the .feature
# file is processed. See the section 'Behaviour Driven Testing' in the 'API
# Reference Manual' chapter of the Squish manual for a comprehensive reference.
#
# The decorators Given/When/Then/Step can be used to associate a script snippet
# with a pattern which is matched against the steps being executed. Optional
# table/multi-line string arguments of the step are passed via a mandatory
# 'context' parameter:
#
#   @When("I enter the text")
#   def whenTextEntered(context):
#      <code here>
#
# The pattern is a plain string without the leading keyword, but a couple of
# placeholders including |any|, |word| and |integer| are supported which can be
# used to extract arbitrary, alphanumeric and integer values resp. from the
# pattern; the extracted values are passed as additional arguments:
#
#   @Then("I get |integer| different names")
#   def namesReceived(context, numNames):
#      <code here>
#
# Instead of using a string with placeholders, a regular expression can be
# specified. In that case, make sure to set the (optional) 'regexp' argument
# to True.

import names


@Given("the app is running")
def step(context):
    startApplication("calqlatr")
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Given("the user is logged in as operator")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("I clear the conveyor 2")
def step(context):
    mouseClick(waitForObject(names.o2_Text))


@Then("the conveyor is clean")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("I put the baggage on the conveyor")
def step(context):
    mouseClick(waitForObject(names.o2_Text))
    mouseClick(waitForObject(names.window_Rectangle), 276, 149, Qt.LeftButton)


@Then("I see the images")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Then("the image is correct")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Given("Calculator is ON")
def step(context):
    startApplication("calqlatr")
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Given("No calculation on going")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Tap 2 on calculator")
def step(context):
    mouseClick(waitForObject(names.o2_Text))


@When("Tap + button")
def step(context):
    mouseClick(waitForObject(names.o_Text))


@When("Press = button")
def step(context):
    mouseClick(waitForObject(names.o_Text_2))


@Then("Check calculator result 4")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Press x button")
def step(context):
    mouseClick(waitForObject(names.o_Text_3))


@Then("Check calculator result 8")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Then("the conveyor is clear")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Tap 1")
def step(context):
    mouseClick(waitForObject(names.o1_Text))


@When("Tap 2")
def step(context):
    mouseClick(waitForObject(names.o2_Text))


@Then("Check calculator result 3")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)

    mouseClick(waitForObject(names.o_Text_3))

    mouseClick(waitForObject(names.o5_Text))

    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Press x")
def step(context):
    mouseClick(waitForObject(names.c_Text))
    mouseClick(waitForObject(names.o3_Text))
    mouseClick(waitForObject(names.o_Text_3))


@When("Tap 5")
def step(context):
    mouseClick(waitForObject(names.o5_Text))


@Then("Check calculator 15")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Given("Machine ON")
def step(context):
    startApplication("calqlatr")
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)

    mouseClick(waitForObject(names.o3_Text))

    mouseClick(waitForObject(names.o_Text))

    mouseClick(waitForObject(names.o4_Text_2))

    mouseClick(waitForObject(names.o_Text_2))

    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Press 3")
def step(context):
    mouseClick(waitForObject(names.c_Text))
    mouseClick(waitForObject(names.o3_Text))


@When("Press +")
def step(context):
    mouseClick(waitForObject(names.o_Text))


@When("Press 4")
def step(context):
    mouseClick(waitForObject(names.o4_Text_2))


@When("Press =")
def step(context):
    mouseClick(waitForObject(names.o_Text_2))


@Then("Check calculator result 7")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@Given("Machine is turning ON")
def step(context):
    startApplication("calqlatr")
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)


@When("Press 50")
def step(context):
    mouseClick(waitForObject(names.o5_Text))
    mouseClick(waitForObject(names.o0_Text))


@Then("Check result 100")
def step(context):
    test.compare(waitForObjectExists(names.o_QQuickView).visible, True)
