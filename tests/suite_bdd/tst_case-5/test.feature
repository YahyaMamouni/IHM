Feature: (Auto)Title of tst_case-5

	Check complex calculation

	Scenario: (Auto)Title of tst_case-5

		#Prerequisites
		Given Machine ON
		

		#Multiple calculation
		When Press 3
		When Press +
		When Press 4
		When Press =
		Then Check calculator result 7
		

