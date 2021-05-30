```sh
gcloud functions deploy slack_to_minecraft \
--runtime python39 \
--region asia-northeast1 \
--timeout 30 \
--trigger-http \
--allow-unauthenticated \
--set-env-vars "PROJECT_ID=YOUR_PROJECT_ID,TOPIC_NAME=YOUR_TOPIC_NAME,SLACK_SECRET=YOUR_SLACK_SECRET"
```
