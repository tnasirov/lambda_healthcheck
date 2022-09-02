import urllib3
import json
import boto3
http = urllib3.PoolManager()

urls = ['https://dev-admin.stage.example.com/actuator/health',
        'https://dev-api.stage.example.com/actuator/health',
        'https://dev-gateway.stage.example.com/actuator/health'
]

slack_webhook = "https://hooks.slack.com/services/xxxxxxxx/xxxxxxxxxxx/xxxxxxxxxxxxxxx"


def lambda_handler(event, context):
    do_health_check()

def do_health_check():
    failures = list()
    for url in urls:
        try:
            response = http.request('GET', url)
            if response.status != 200:
                error = dict()
                temp=url.split('://')
                error['url'] = '('+temp[0]+') '+temp[1]
                error['status'] = response.status
                error['response'] = response.data
                failures.append(error)
        except e:
            error = dict()
            temp=url.split('://')
            error['url'] = '('+temp[0]+') '+temp[1]
            error['status'] = 'xxx'
            error['response'] = e
            failures.append(error)
            message = "Error occurred for url: " + error['url']+ ". Error: " + e
            print(message)
            
    if len(failures) > 0:
        message = "Health check failures in following. \n\n"
        for failure in failures:
            message += repr(failure) + '\n'
        print('Sending message:'+ message)
        #Publish to Slack Channel
        data = {"text": message}
        
        r = http.request("POST",
                         slack_webhook,
                         body = json.dumps(data),
                         headers = {"Content-Type": "application/json"})
