Feature: (AUTO)Title of tst_case-3

	Check complex calculation

	Scenario: (AUTO)Title of tst_case-3

		#Multiple calculation
		Given Calculator is ON
		Given No calculation on going
		## Additions
		When Tap 2 on calculator 'testing'
		When Tap + button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 4 
			"""
			- 2 <Emergency Buttons> are 'easily accessible'
			- 2 <Emergency Buttons> are 'push buttons'
			"""
		## Multiplication
		When Press x button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 8 
			"""
			- 2 <Normal Buttons> are 'push buttons'
			"""
		

