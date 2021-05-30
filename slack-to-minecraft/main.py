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

import json
import os

from flask import jsonify
from google.cloud import pubsub_v1
from slack.signature import SignatureVerifier


PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_NAME = os.getenv('TOPIC_NAME')
SLACK_SECRET = os.getenv('SLACK_SECRET')

publisher = pubsub_v1.PublisherClient()


def verify_signature(request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(SLACK_SECRET)

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError('Invalid request/credentials.')


def format_slack_message(message):
    message = {
        'response_type': 'in_channel',
        'text': message
    }
    return jsonify(message)


# Publishes a message to a Cloud Pub/Sub topic.
def slack_to_minecraft(request):
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    verify_signature(request)

    text = request.form['text']
    response_url = request.form['response_url']

    print(f'Publishing message to topic {TOPIC_NAME}')

    # References an existing topic
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

    message_json = json.dumps({
        'text': text,
        'response_url': response_url
    })
    message_bytes = message_json.encode('utf-8')

    # Publishes a message
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return format_slack_message('')
    except Exception as e:
        print(f'Message publishing failed. {e}')
        return format_slack_message(f'メッセージのpublishingに失敗したよ！{e}')
