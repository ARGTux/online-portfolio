import os
import git
from pathlib import Path

# Base directory of the Streamlit app (assumes this file lives in the project root)
BASE_DIR = Path(__file__).parent


def git_push_changes(commit_message: str = "Update portfolio data") -> None:
    """Stage all changes, commit with the provided message, and push to origin.

    This function uses a personal access token (PAT) taken from the environment variable
    ``GITHUB_TOKEN``. If the token is not set, the push will be attempted using the default
    remote URL configuration (which may fail in the Streamlit Cloud environment).
    """
    try:
        repo = git.Repo(str(BASE_DIR))
    except Exception as e:
        raise RuntimeError(f"Failed to locate git repository at {BASE_DIR}: {e}")

    # Stage all changes
    repo.git.add(A=True)

    # Commit
    repo.index.commit(commit_message)

    # Push using token if available
    origin = repo.remote(name="origin")
    token = os.getenv("GITHUB_TOKEN")
    if token:
        # Construct authenticated URL (preserve original repo path)
        raw_url = origin.url
        if raw_url.startswith("https://"):
            # Insert token after https://
            auth_url = raw_url.replace("https://", f"https://{token}@")
        else:
            # Fallback to token-less URL
            auth_url = raw_url
        # Update remote URL temporarily for this push
        try:
            origin.set_url(auth_url)
            origin.push()
        finally:
            # Reset remote URL to original to avoid persisting token in repo config
            origin.set_url(raw_url)
    else:
        # No token; attempt default push (may rely on existing auth config)
        origin.push()
