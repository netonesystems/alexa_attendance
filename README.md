# Alexa Attendance System

## What's This?

This application will allow to regist your attendance information in your work scene.

e.g.)
```
You 「アレクサ、○○で××さんを登録して」
Alexa「××さんの勤怠ですね。勤怠の種類は出社ですか退社ですか?」
You 「出社で登録」
Alexa 「××さんの 出社 を登録しました。」
```

## How to
### Requirements
Serverless Framework v1.27.3 or later

### Install dependancies
> pip install -r requirements.txt

### Configure serverlesss YAML
```
  environment:
    TZ: Asia/Tokyo
    WEBEX_ROOM_ID: <YOUR_ROOM_ID>
    WEBEX_ACCESS_TOKEN: <YOUR_ACCESS_TOKEN>

functions:
  alexxa_attendance:
    handler: alexa_attendance.lambda_handler

    events:
      - alexaSkill: <YOUR_ALEXA_SKILL_ID>
```

### Deploy with Your AWS Account
> sls deploy

### Test Your Function
WIP
