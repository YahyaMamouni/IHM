Feature: (Auto)Title of tst_case-7

	Check complex calculation

	Scenario: (Auto)Title of tst_case-7

		#Prerequisites
		Given ON
		

		#calculation
		When Press 39
		When Press +
		When Press 1
		When Press +
		When Press 60
		When Press equal
		Then Check result 100
		

