Feature: (AUTO)Title of tst_case-2

	Check complex calculation

	Scenario: (AUTO)Title of tst_case-2

		#Multiple calculation
		Given Calculator is ON
		Given calculation on going
		## Additions
		When Tap 2 on 'testing'
		When Tap + button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 4 
			"""
			- 2 <Emergency Buttons> are 'easily accessible'
			"""
		## Multiplication
		When Press + button
		When Tap 2 on calculator
		When Press = button
		Then Check calculator result 8 
			"""
			- 2 <Normal Buttons> are 'push buttons'
			"""
		Then Check calculator result 8 
			"""
			- 2 <Normal Buttons> are 'push buttons'
			- <Exceptional Button> 'emergency buttons'
			"""
		

