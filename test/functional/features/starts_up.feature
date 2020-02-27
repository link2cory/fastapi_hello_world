@smoke_test 
Feature: Application Starts Up Successfully
  as a developer,
  I want to know that the application starts up successfully
  So I can tell if my project was set up properly
  
  Scenario: The application responds to requests
    Given the user makes a request
    Then the server responds
