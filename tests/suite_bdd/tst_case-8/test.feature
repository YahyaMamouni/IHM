Feature: (Auto)Title of tst_case-8

	Check complex calculation

	Scenario: (Auto)Title of tst_case-8

		#Prerequisites
		Given Selecting Machine
		

		#calculation
		## Entering numbers
		When Press 39
		## Pressing the plus button
		When Press +
		## Entering another numbers
		When Press 1
		When Press +
		When Press 60
		When Press equal
		Then Check result 100
		

