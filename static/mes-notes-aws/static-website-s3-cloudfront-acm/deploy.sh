#!/bin/bash -xe

export AWS_PROFILE=sdenel-perso-root

aws2 cloudformation validate-template --template-body file://static-website.yaml

# switch between update-stack and create-stack
aws2 cloudformation update-stack \
--tags Key=app,Value=blog \
--stack-name blog \
--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
--parameters "ParameterKey=HostedZoneId,ParameterValue=ZTC85MOA8LX7D" \
--template-body file://static-website.yaml
