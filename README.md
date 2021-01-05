# Trend Micro Cloud One Conformity Scanner

This GitHub repo sets up an integration with GitHub and Trend Micro Cloud One Conformity Template Scanner. 

Everytime there is a commit pushed to the configured GitHub repo, the commit is parsed for supported file formats (`json`, `yaml`, or `yml`) and checks if the file is an AWS CloudFormation template.

If it is an AWS CloudFormation template, it posts the file to the *Cloud One Conformity Template Scanner API* to retrieve scan results and create GitHub Issues with the scan results.

### Deploy CloudFormation template
---

An AWS CloudFormation template to deploy API Gateway REST API (POST) Endpoint, AWS Lambda and required resources.

### Required fields


 - #### **ConformityApiKey**
        
An API key is required to authenticate requests to the Template Scanner API. You can create an API Key to access Cloud One Conformity APIs by following Conformity documentation provided here - https://www.cloudconformity.com/help/public-api/api-keys.html.
        
> For more information on Cloud One Conformity APIs, please refer to the API reference documentation available here - https://cloudone.trendmicro.com/docs/conformity/api-reference/

- #### **GitHubToken**
        
You will need a personal access token from GitHub to integrate Cloud One Conformity Template scan results within the GitHub repository. You can obtain this personal access token by following the steps provided in this GitHub Doc - https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token

> The **Outputs** section of the newly created CloudFormation Stack contains the API Endpoint URL that needs to be configured as the GitHub Webhook for the repository.

### Cloud One Conformity Template Scanner
---

Lambda function written in Python to configure the GitHub repository via GitHub APIs -

- Create Labels
- Create Issues
- Create Tags (WIP)

> For more information on GitHub APIs, please refer to the API reference documentation available here - https://docs.github.com/en/free-pro-team@latest/rest/reference

### Sample CloudFormation Template
---

The `sample_cloudformation_template.json` file is provided to upload to a configured GitHub repository.


## How to deploy
---

- Run the CloudFormation template on AWS. Retrieve the `API Endpoint URL` from the `Outputs` tab.

- Configure GitHub Repository for webhooks
    - Navigate to your `GitHub Repository > Settings > Webhooks`
    - Enter the API Endpoint URL from the CloudFormation Stack as the `Payload URL`
    - Set the Content Type to `application/json`
    - Choose `Just the push event` under "Which events would you like to trigger this webhook?"
    - Mark the webhook as `Active`
    - Click `Add webhook`

- Commit the `sample_cloudformation_template.json` to the configured GitHub repo.

- Navigate to the `Issues` tab on the GitHub repo, to see the results of the scan.

- You can now filter the issues with GitHub Labels.
    - The supported Cloud One Conformity labels are `EXTREME`, `VERY_HIGH`, `HIGH`, `MEDIUM` and `LOW`