# Standard
import json
import os
import sys

# AWS provided
import boto3

# Vendor
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
FSO_RSS_ID = os.environ["FSO_RSS_ID"]
FSO_BOX_ID = os.environ["FSO_BOX_ID"]

ec2_client = boto3.client("ec2")


def reply(chat_id, message):
    data = {"text": message.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    requests.post(url, data)


def m_hello(chat_id):
    reply(chat_id, "Hi")


def ec2_instance(chat_id, instance_id):
    response = ec2_client.describe_instances(
        InstanceIds=[
            instance_id,
        ]
    )

    print(response)
    msg = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            state = instance["State"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            msg.append({"state": state, "type": instance_type, "ip": public_ip})

    reply(chat_id, json.dumps(msg))


def m_box_instance(chat_id):
    ec2_instance(chat_id, FSO_BOX_ID)


def ec2_status(chat_id, instance_id):
    response = ec2_client.describe_instance_status(
        IncludeAllInstances=True,
        InstanceIds=[
            instance_id,
        ],
    )
    status = response["InstanceStatuses"][0]["InstanceState"]
    reply(chat_id, json.dumps(status))


def m_rss_status(chat_id):
    ec2_status(chat_id, FSO_RSS_ID)


def m_box_status(chat_id):
    ec2_status(chat_id, FSO_BOX_ID)


def ec2_start(chat_id, instance_id):
    response = ec2_client.start_instances(
        InstanceIds=[
            instance_id,
        ]
    )
    status = response["StartingInstances"]
    reply(chat_id, json.dumps(status))


def m_start_rss(chat_id):
    ec2_start(chat_id, FSO_RSS_ID)


def m_start_box(chat_id):
    ec2_start(chat_id, FSO_BOX_ID)


def ec2_stop(chat_id, instance_id):
    response = ec2_client.stop_instances(
        InstanceIds=[
            instance_id,
        ]
    )
    status = response["StoppingInstances"]
    reply(chat_id, json.dumps(status))


def m_stop_rss(chat_id):
    ec2_stop(chat_id, FSO_RSS_ID)


def m_stop_box(chat_id):
    ec2_stop(chat_id, FSO_BOX_ID)


mux = {
    "/Hello": m_hello,
    "/rssstatus": m_rss_status,
    "/boxstatus": m_box_status,
    "/box": m_box_instance,
    "/startrss": m_start_rss,
    "/stoprss": m_stop_rss,
    "/startbox": m_start_box,
    "/stopbox": m_stop_box,
}


def handler(event, context):
    try:
        print(json.dumps(event))
        body = event["body"]
        command = str(body["message"]["text"])
        chat_id = body["message"]["chat"]["id"]
        first_name = body["message"]["from"]["first_name"]
        print("command", command)

        if command in mux:
            mux[command](chat_id)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
