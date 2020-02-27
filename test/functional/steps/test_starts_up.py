from pytest_bdd import scenarios, parsers, given, when, then

import pytest


scenarios('../features/starts_up.feature')

@given('the user makes a request')
def response(client):
    return client.get('/')

@then('the server responds')
def verify_response(response):
    # the fact that we got here is all that matters
    pass

