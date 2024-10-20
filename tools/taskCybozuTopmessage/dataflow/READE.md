# テンプレート作成コマンド
mvn compile exec:java \
-Dexec.mainClass=com.google.cloud.teleport.templates.DatastoreToPubsub \
-Dexec.cleanupDaemonThreads=false \
-Dexec.args=" \
--project=tfounion-cfcb3 \
--stagingLocation=gs://data_flow_template/staging \
--tempLocation=gs://data_flow_template/temp \
--templateLocation=gs://data_flow_template/templates/cybozuusers_ds_pubsub.json \
--runner=DataflowRunner"


# ErrorTagが無いエラーの対応
https://stackoverflow.com/questions/51890285/how-to-use-google-provided-template-pubsub-to-datastore