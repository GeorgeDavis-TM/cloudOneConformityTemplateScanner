import os
import json
import urllib3
import datetime

def githubLabelsApi(http, githubApiUrl):
    labels = {
        "EXTREME": "B60205",
        "VERY_HIGH": "B60205",
        "HIGH": "B60205",
        "MEDIUM": "D93F0B",
        "LOW": "FBCA04"
    }
    header = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PostmanRuntime/7.26.8",
        "Authorization": "token " + str(os.environ.get('GITHUB_TOKEN'))
    }
    for label in labels:
        data = {
            "name": label,
            "color": labels[label],
            "description": "Trend Micro Cloud One Conformity - " + label
        }
        r = http.request('POST', githubApiUrl + "/labels", headers=header, body=json.dumps(data))
        print(str(r.data))

def githubIssuesApi(http, githubHtmlUrl, githubApiUrl, commit, filename, reportTitle, reportSummaryList, reportDetail):
    header = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PostmanRuntime/7.26.8",
        "Authorization": "token " + str(os.environ.get('GITHUB_TOKEN'))
    }
    data = {
        "title": "Cloud Conformity Template Scanner Report for " + filename + ":" + commit["id"],
        "body": "# Cloud Conformity Template Scanner Report for [" + filename + "](" + githubHtmlUrl + "/blob/" + commit["id"] + "/" + filename + ")\n### Commit ID - " + commit["id"] + "\n### Issues Summary - \n" + reportTitle.replace(" ", "\n").replace(":", ": ") + "\n### List of Trend Micro Cloud One Conformity Issues are as below.\n```" + str(json.dumps(reportDetail, indent=4, sort_keys=True)) + "```",
        "labels": reportSummaryList
    }
    r = http.request('POST', githubApiUrl + "/issues", headers=header, body=json.dumps(data))
    print(str(r.data))
    return {
        'headers': { "Content-type": "application/json" },
        'statusCode': 200,
        'body': str(r.data)
    }

def githubTaggerApi(http, githubApiUrl, commit, tagValue):
    header = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PostmanRuntime/7.26.8",
        "Authorization": "token " + str(os.environ.get('GITHUB_TOKEN'))
    }
    data = {
        "tag": str(tagValue),
        "object": commit["id"],
        "message": "Cloud Conformity Template Scanner Report - https://us-west-2.cloudconformity.com/template-scanner",
        "tagger": {
            "name": commit["committer"]["name"],
            "email": commit["committer"]["email"],
            "date": commit["timestamp"]
        },
        "type": "commit"
    }
    r = http.request('POST', githubApiUrl + "/git/tags", headers=header, body=json.dumps(data))
    print(str(r.data))
    return {
        'headers': { "Content-type": "application/json" },
        'statusCode': 200,
        'body': str(r.data)
    }
    
def postConformityApi(ccApiKey, http, githubHtmlUrl, githubApiUrl, commit, filename, githubFileString):
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "ApiKey " + ccApiKey
    }
    data = {
        "data": {
            "attributes": {
                "type": "cloudformation-template",
                "contents": githubFileString
            }
        }
    }
    r = http.request('POST', 'https://us-west-2-api.cloudconformity.com/v1/template-scanner/scan', headers=headers, body=json.dumps(data))
    responseDict = json.loads(r.data)
    reportDict = {}
    for data in responseDict["data"]:
        if data["type"] == "checks":
            if str(data["attributes"]["risk-level"]) not in reportDict:
                reportDict.update({ data["attributes"]["risk-level"]: 1 })
            else:
                reportDict.update({ data["attributes"]["risk-level"]: reportDict[data["attributes"]["risk-level"]] + 1 })
    reportList = []
    reportTitle = ""
    for severity in reportDict:
        reportList.append(severity)
        reportTitle += severity + ":" + str(reportDict[severity]) + " "
    githubIssuesApi(http, githubHtmlUrl, githubApiUrl, commit, filename, reportTitle, reportList, responseDict)
    return reportDict
        
def processJsonFile(ccApiKey, http, githubHtmlUrl, githubRawFileUrl, githubApiUrl, commit, filename):
    githubFileString = ""
    r = http.request('GET', githubRawFileUrl)
    githubFileString = (r.data).decode("utf-8")
    cfJsonDict = json.loads(githubFileString)
    if "AWSTemplateFormatVersion" in cfJsonDict:
        response = postConformityApi(ccApiKey, http, githubHtmlUrl, githubApiUrl, commit, filename, str(githubFileString))
        for severity in response:
            githubTaggerApi(http, githubApiUrl, commit, str(severity))
        
def processYamlFile(ccApiKey, http, githubHtmlUrl, githubRawFileUrl, githubApiUrl, commit, filename):
    githubFileString = ""
    r = http.request('GET', githubRawFileUrl)
    githubFileString = (r.data).decode("utf-8")
    if "AWSTemplateFormatVersion" in githubFileString:
        response = postConformityApi(ccApiKey, http, githubHtmlUrl, githubApiUrl, commit, filename, str(githubFileString))
        for severity in response:
            githubTaggerApi(http, githubApiUrl, commit, str(severity))

def lambda_handler(event, context):
    ccApiKey = str(os.environ.get('CC_API_KEY'))
    supportedFileExtensions = ["json", "yaml", "yml"]
    print("\nEvent: " + str(event))
    print("\nContext: " + str(context))
    httpBody = json.loads(event["body"])
    githubApiUrl = "https://api.github.com/repos/" + httpBody["repository"]["full_name"]
    githubHtmlUrl = httpBody["repository"]["html_url"]
    http = urllib3.PoolManager()
    githubLabelsApi(http, httpBody["repository"])
    filesInvolved = []
    for commit in httpBody["commits"]:
        filesInvolved = commit["added"] + commit["modified"]
        print(str(filesInvolved))
        for filename in filesInvolved:
            if ccApiKey != "" and filename.split(".")[-1].lower() in supportedFileExtensions:
                githubRawFileUrl = "https://raw.githubusercontent.com/" + httpBody["repository"]["full_name"] + "/" + commit["id"] + "/" + filename
                if filename.split(".")[-1].lower() == "json":
                    processJsonFile(ccApiKey, http, githubHtmlUrl, githubRawFileUrl, githubApiUrl, commit, filename)
                elif filename.split(".")[-1].lower() == "yaml" or filename.split(".")[-1].lower() == "yml":
                    processYamlFile(ccApiKey, http, githubHtmlUrl, githubRawFileUrl, githubApiUrl, commit, filename)
            else:
                print(str("Not a supported file."))