```sh
gcloud functions deploy operate_minecraft_instance \
--runtime python39 \
--region asia-northeast1 \
--timeout 60 \
--trigger-topic YOUR_TOPIC_NAME \
--set-env-vars "PROJECT_ID=YOUR_PROJECT_ID,ZONE=YOUR_ZONE,INSTANCE_NAME=YOUR_INSTANCE_NAME"
```
