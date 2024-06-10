import boto3
import os 

build = boto3.client('codebuild')
commit = boto3.client('codecommit')

def lambda_handler(event, context):
    
    #get details of code build result
    if event["detail"]["event"] == "pullRequestCreated" or event["detail"]["event"] == "pullRequestSourceBranchUpdated":
        
        targetBranch = event["detail"]["destinationReference"].split('/')[2]
        sourceBranch = event["detail"]["sourceReference"].split('/')[2]

        build_Var = [
                        {
                              'name': 'pullRequestId',
                              'value': event["detail"]["pullRequestId"],
                              'type': 'PLAINTEXT'
                        },
                        {
                              'name': 'targetBranch',
                              'value': targetBranch,
                              'type': 'PLAINTEXT'
                        },
                        {
                              'name': 'sourceBranch',
                              'value': sourceBranch,
                              'type': 'PLAINTEXT'
                        },
                        {
                              'name': 'destinationCommit',
                              'value': event["detail"]["destinationCommit"],
                              'type': 'PLAINTEXT'
                        },
                        {
                              'name': 'sourceCommit',
                              'value': event["detail"]["sourceCommit"],
                              'type': 'PLAINTEXT'
                        },
                        {
                              'name': 'repositoryName',
                              'value': event["detail"]["repositoryNames"][0],
                              'type': 'PLAINTEXT'
                        }]

    #start code build with updated parameters from the pull request event
        startBuild_1 = build.start_build(
                    projectName=os.environ['TERRAFORMBUILD_PROJECT_NAME'],
                    sourceLocationOverride="https://git-codecommit." + os.environ['AWS_REGION'] + ".amazonaws.com/v1/repos/" + event["detail"]["repositoryNames"][0],
                    artifactsOverride={'type': 'NO_ARTIFACTS'},
                    sourceVersion=sourceBranch,
                    sourceTypeOverride='CODECOMMIT',
                    environmentVariablesOverride=build_Var
                    )
        
        print(startBuild_1)

        startBuild_2 = build.start_build(
                    projectName=os.environ['ACCESSANALYZERCHECKS_PROJECT_NAME'],
                    sourceLocationOverride="https://git-codecommit." + os.environ['AWS_REGION'] + ".amazonaws.com/v1/repos/" + event["detail"]["repositoryNames"][0],
                    artifactsOverride={'type': 'NO_ARTIFACTS'},
                    sourceVersion=sourceBranch,
                    sourceTypeOverride='CODECOMMIT',
                    environmentVariablesOverride=build_Var
                    )
                    
        print(startBuild_2)