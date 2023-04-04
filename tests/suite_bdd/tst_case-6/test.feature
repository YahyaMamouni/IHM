Feature: (Auto)Title of tst_case-6

	Check complex calculation

	Scenario: (Auto)Title of tst_case-6

		#Prerequisites
		Given Machine is turning ON
		

		#calculation
		When Press 50
		When Press +
		When Press 50
		When Press =
		Then Check result 100
		

