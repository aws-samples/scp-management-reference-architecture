import hashlib
import logging
import os
from github import Github
from github.GithubException import UnknownObjectException

# Set Log Level
logging.basicConfig(level=logging.INFO)


def calculate_sha1(file_path):
    # Works for files up to 1 MB in size. Beyond that, use iter and chunk it
    with open(file_path, "rb") as file_for_hash:
        data = file_for_hash.read()
        filesize = len(data)
    full_string = "blob " + str(filesize) + "\0" + data.decode("utf-8")
    logging.debug(f"Full string: {full_string}")
    return hashlib.sha1(full_string.encode("utf-8")).hexdigest()


def commit_local_files_not_in_remote(
    # Local folder to walk through to check for changed files
    root_folder,
    # The full identifier (including GH Org) of the repository
    repository,
    # The feature branch name to commit to
    feature_branch,
    main_branch="main",
):
    # Loop over all files in the service_control_policies folder and find any files that exist locally but not remotely.
    # Commit the local files and create a PR if necessary
    # Note: Requires a bot/app token like GITHUB_TOKEN, NOT A PAT.
    repo_token = os.getenv("GITHUB_TOKEN")
    gh = Github(repo_token)
    remote_repo = gh.get_repo(repository)

    # Create the branch if necessary
    try:
        remote_repo.get_branch(feature_branch)
    except Exception:
        sb = remote_repo.get_branch(main_branch)
        remote_repo.create_git_ref(
            ref="refs/heads/" + feature_branch,
            sha=sb.commit.sha,
        )

    found_changed_file = False
    for root, _, files in os.walk(root_folder):
        for file in files:
            update_this_file = False
            file_path = os.path.join(root, file)
            print(f"Checking {file_path}")
            # Get the SHA of the file in the main branch, if it exists.
            try:
                file_content = remote_repo.get_contents(
                    path=file_path,
                    ref=main_branch,
                )
                logging.debug(f"File content: {file_content.decoded_content}")
                remote_sha = file_content.sha
            except UnknownObjectException:
                print(f"File {file_path} does not exist in main branch.")
                update_this_file = True
                remote_sha = None
            else:
                logging.info(f"File {file_path} exists in main branch.")

            # Get the SHA of the file in the feature branch, if it exists.
            try:
                file_feature_content = remote_repo.get_contents(
                    path=file_path,
                    ref="refs/heads/" + feature_branch,
                )
                logging.debug(f"File content: {file_content.decoded_content}")
                feature_sha = file_feature_content.sha
            except UnknownObjectException:
                logging.info(f"File {file_path} does not exist in feature branch.")
                feature_sha = None
                update_this_file = True
            else:
                logging.info(f"File {file_path} exists in feature branch.")

            # Get the SHA of the file in the local folder.
            local_sha = calculate_sha1(
                file_path=file_path,
            )
            # Check if the local file has the same contents as the feature and main branches.
            if feature_sha == local_sha:
                print(
                    f"File {file_path} already has the same contents as the feature branch. Skipping commit."
                )
                continue
            if local_sha == remote_sha:
                print(
                    f"File {file_path} has the same contents as the main branch. Skipping commit."
                )
                continue
            else:
                update_this_file = True
                print(f"File {file_path} has different contents than the main branch.")

            # Update the file
            if update_this_file:
                logging.warning(f"Feature SHA: {feature_sha}")
                logging.warning(f"Local SHA: {local_sha}")
                logging.warning(f"Main SHA: {remote_sha}")
                found_changed_file = True
                with open(file_path, "r") as f:
                    file_contents = f.read()
                commit_message = f"Update {file_path}"
                if feature_sha is None:
                    response = remote_repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=file_contents,
                        branch=feature_branch,
                    )
                else:
                    response = remote_repo.update_file(
                        path=file_path,
                        message=commit_message,
                        content=file_contents,
                        sha=feature_sha,
                        branch=feature_branch,
                    )
                print(f"Commit sha: {response['commit'].sha}")

    if found_changed_file is False:
        print("No changes required -- skipping pull request creation.")
        return
    remote_repo.create_pull(
        base=main_branch,
        head=feature_branch,
        title="Auto-update OU structure",
        body="Updating SCP structure to reflect OU/account changes in the Organization",
    )
    return


if __name__ == "__main__":
    commit_local_files_not_in_remote(
        root_folder="service_control_policies",  # reference is relative to the repo root
        repository="realmidx/terraform_aws_scp_manager",
        feature_branch="feature/scp-ou-structure-update",
    )
    print("Done")
