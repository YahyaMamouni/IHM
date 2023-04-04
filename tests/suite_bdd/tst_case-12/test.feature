Feature: (AUTO) Test modifying BDD file

	Objectives : 
	
	Testing modifying the BDD file

	Scenario: (AUTO) Test modifying BDD file

		#Scan baggage 2
		Given the app is running
		Given the user is logged in as operator
		## We want to scan the baggage 2
		## Handle conveyor
		When I clear the conveyor 2
		Then the conveyor is clear 
			"""
			- 2
			"""
		When I put the baggage on the conveyor
		

		#Get baggage's images
		Then I see the images 
			"""
			- 2
			"""
		

