# coding:utf-8

"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function

import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('attendance')

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "勤怠システム"
    speech_output = "勤怠システムでは特定の人の出社、退社時間を記録することができます。" \
                    "登録したい人の名前または出社、退社どちらを登録したいかもしくはその両方を教えてください。"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "登録したい人の名前または出社、退社どちらを登録したいかもしくはその両方を教えてください。"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def register_attendance(person, type):
    today = datetime.today()
    date = today.strftime("%Y-%m-%dT%H:%M:%S+0900")
        
    table.put_item(
        Item = {
            "uuid": str(uuid.uuid1()),
            "name": person,
            "type": type,
            "date": date
        }
    )

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def set_attributes(session_attributes, key, value):
    session_attributes[key] = value
    
def set_attendance_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = "勤怠管理"
    session_attributes = {}
    should_end_session = True

    if 'person' in intent['slots'] and 'type' in intent['slots']:
        person = intent['slots']['person']['value']
        type = intent['slots']['type']['value']
        
        set_attributes(session_attributes, "Person", person)
        set_attributes(session_attributes, "Type", type)
     
        speech_output = person + \
                        "さんの" + type + "を登録しました。 "
        reprompt_text = None

        # Add attendance info DynamoDB        
        register_attendance(person, type)
    else:
        speech_output = "もう一度試してください。"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_person_in_session(intent, session):
    card_title = "勤怠管理"
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    else:
        session_attributes = {}
    should_end_session = False
    reprompt_text = None

    if 'person' in intent['slots']:
        person = intent['slots']['person']['value']
        
        set_attributes(session_attributes, "Person", person)
        
        if "Person" in session_attributes and "Type" in session_attributes:
            type = session_attributes["Type"]
            
            speech_output = person + \
                            "さんの" + \
                            type + \
                            "を登録しました。 "
            reprompt_text = None
            today = datetime.today()
            date = today.strftime("%Y-%m-%dT%H:%M:%S+0900")
        
            table.put_item(
            Item = {
                    "uuid": str(uuid.uuid1()),
                    "name": person,
                    "type": type,
                    "date": date
                }
            )
        else:
            speech_output = person + \
                            "さんの勤怠ですね。" \
                            "勤怠の種類は出社ですか退社ですか?"
            reprompt_text = "勤怠の種類を教えてください。"
    else:
        speech_output = "もう一度誰の勤怠を登録するか教えてください。"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_type_in_session(intent, session):
    card_title = "勤怠管理"
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    else:
        session_attributes = {}
    should_end_session = False

    if 'type' in intent['slots']:
        type = intent['slots']['type']['value']
        
        set_attributes(session_attributes, "Type", type)
        
        if "Person" in session_attributes and "Type" in session_attributes:
            person = session_attributes["Person"]
            
            speech_output = person + \
                        "さんの" + type + "を登録しました。 "
            reprompt_text = None
            should_end_session = True
        else:
            speech_output = type + \
                            "を登録ですね。" \
                            "誰の勤怠を登録しますか?"
            reprompt_text = "誰の勤怠を登録するか教えてください。"
    else:
        speech_output = "もう一度勤怠の種類を教えてください。"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PersonTypeIntent":
        return set_attendance_in_session(intent, session)
    elif intent_name == "PersonIntent":
        return set_person_in_session(intent, session)
    elif intent_name == "TypeIntent":
        return set_type_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
