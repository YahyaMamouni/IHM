Feature: (Auto)Title of tst_case-3

	Check complex calculation

	Scenario: (Auto)Title of tst_case-3

		#Prerequisites
		Given Calculator is ON
		Given No calculation on going
		

		#Multiple calculation
		## Additions
		When Tap 2 on calculator
		When Tap + button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 4
		## Multiplication
		When Press x button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 8
		

