https://dataflow.googleapis.com/v1b3/projects/tfounion-cfcb3/templates:launch?gcsPath=gs://data_flow_template/templates/cybozuusers_ds_pubsub.json
{
    "jobName": "cybozuUser_datastore2Pubsub",
    "parameters": {
        "datastoreReadProjectId" : "tfounion-cfcb3",
        "datastoreReadGqlQuery": "SELECT * FROM cybozu_account",
        "pubsubWriteTopic" : "projects/tfounion-cfcb3/topics/cybozu_users"
     },
     "environment": {
         "tempLocation": "gs://data_flow_template/temp",
         "zone": "asia-northeast1-a"
     }
}
