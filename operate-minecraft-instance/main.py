# Copyright 2018, Google, LLC.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import time
import os
import traceback

import requests
import googleapiclient.discovery


PROJECT_ID = os.getenv('PROJECT_ID')
ZONE = os.getenv('ZONE')
INSTANCE_NAME = os.getenv('INSTANCE_NAME')
MINECRAFT_PORT = os.getenv('MINECRAFT_PORT')

compute = googleapiclient.discovery.build('compute', 'v1')


def post_slack_message(response_url, message):
    headers = {'content-type': 'application/json'}
    data = json.dumps({
        'response_type': 'in_channel',
        'text': message
    })
    requests.post(
        url=response_url,
        data=data,
        headers=headers
    )


def get_instance():
    response = compute.instances().get(
        project=PROJECT_ID,
        zone=ZONE,
        instance=INSTANCE_NAME
    ).execute()
    return response


def ip_address_from_response(response):
    status = response['status']
    address = response['networkInterfaces'][0]['accessConfigs'][0]['natIP'] if status == 'RUNNING' else ''
    return f'\nIPアドレス： `{address}:{MINECRAFT_PORT}`' if len(address) > 0 else ''


def status_instance(response_url):
    response = get_instance()
    status = response['status']
    message = f'現在のインスタンスの状態は {status} だよ！{ip_address_from_response(response)}'

    post_slack_message(response_url, message)


def start_instance(response_url):
    post_slack_message(response_url, 'インスタンスを起動するよ！')

    compute.instances().start(
        project=PROJECT_ID,
        zone=ZONE,
        instance=INSTANCE_NAME
    ).execute()
    response = get_instance()

    loop_count = 0
    while response['status'] != 'RUNNING':
        if loop_count >= 10:
            post_slack_message(response_url, '処理に時間がかかっているから後はGCPコンソールで確認してね')
            return

        time.sleep(5)
        response = get_instance()
        loop_count += 1

    post_slack_message(response_url, f'インスタンスを起動したよ！{ip_address_from_response(response)}')


def stop_instance(response_url):
    post_slack_message(response_url, 'インスタンスを停止するよ！')

    compute.instances().stop(
        project=PROJECT_ID,
        zone=ZONE,
        instance=INSTANCE_NAME
    ).execute()
    response = get_instance()

    loop_count = 0
    while response['status'] != 'TERMINATED':
        if loop_count >= 10:
            post_slack_message(response_url, '処理に時間がかかっているから後はGCPコンソールで確認してね')
            return

        time.sleep(5)
        response = get_instance()
        loop_count += 1

    post_slack_message(response_url, 'インスタンスを停止したよ！')


# Triggered from a message on a Cloud Pub/Sub topic.
def operate_minecraft_instance(event, context):
    req = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    text = req['text']
    response_url = req['response_url']

    try:
        if text == 'status':
            status_instance(response_url)
        elif text == 'start':
            start_instance(response_url)
        elif text == 'stop':
            stop_instance(response_url)
        else:
            post_slack_message(response_url, '[status|start|stop]以外のリクエストは受け付けられないよ！')
    except Exception as e:
        print(f'Minecraft instance operation failed. {e}')
        traceback.print_exc()
        message = '処理中に例外が発生したよ！\n'
        message += str(e)
        post_slack_message(response_url, message)
