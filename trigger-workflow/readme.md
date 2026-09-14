# Trigger Workflow Action

This GitHub composite action triggers a workflow in a specified repository and monitors its execution until completion.

## 📋 Description

This action automates the process of:
1. Triggering a workflow in a target repository
2. Waiting for the workflow run to be created
3. Monitoring the workflow execution
4. Reporting the final status

## 📥 Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `gh-token` | GitHub token with permissions to trigger workflows and read workflow runs | ✅ Yes | - |
| `workflow-name` | Name of the workflow file to trigger (e.g., `build.yml`) | ✅ Yes | - |
| `repository` | The repository where the workflow is located (format: `owner/repo`) | ✅ Yes | - |
| `ref` | The git reference (branch, tag, or SHA) to run the workflow on | ✅ Yes | - |
| `time-interval-seconds` | Time interval in seconds between workflow status checks | ❌ No | `10` |


## 🚀 Usage

### Basic Example

```yaml
jobs:
  trigger-build:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger and monitor workflow
        uses: ansys/saf-devops/trigger-workflow@v1
        with:
          gh-token: ${{ secrets.WORKFLOW_TOKEN }}
          workflow-name: build.yml
          repository: ansys/my-repo
          ref: main
```

### Advanced Example with Custom Polling Interval

```yaml
jobs:
  trigger-test:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger test workflow
        id: trigger
        uses: ansys/saf-devops/trigger-workflow@v1
        with:
          gh-token: ${{ secrets.WORKFLOW_TOKEN }}
          workflow-name: test-suite.yml
          repository: ansys/test-repo
          ref: develop
          time-interval-seconds: 30

      - name: Check result
        if: always()
        run: |
          echo "Workflow status: ${{ steps.trigger.outputs.status }}"
```

## ⚙️ How It Works

1. **Trigger Workflow**: The action triggers the specified workflow in the target repository using the GitHub CLI (`gh workflow run`).

2. **Wait for Run Creation**: The action polls the GitHub API (up to 12 attempts, 10 seconds apart) to find the newly created workflow run.

3. **Monitor Execution**: Once found, the action continuously checks the workflow status at the specified interval until completion.

4. **Report Status**: The action exits with:
   - ✅ Exit code `0` if the workflow succeeds
   - ❌ Exit code `1` if the workflow fails or cannot be found

## 🔐 Token Requirements

The `gh-token` must have the following permissions:
- `actions:read` - To view workflow runs
- `actions:write` - To trigger workflows
- Repository access to the target repository

## ⚠️ Notes

- The action assumes the GitHub CLI (`gh`) is available (pre-installed on GitHub-hosted runners)
- The workflow run detection has a maximum of 12 attempts (120 seconds total wait time)
- The action provides real-time status updates in the workflow logs
- A direct link to the triggered workflow run is displayed in the logs

## 📝 Example Output

```
🚀 Triggering workflow 'build.yml' in ansys/my-repo on ref 'main'
✅ Found workflow run: 1234567890
⏳ Monitoring workflow execution...
[build.yml] ⏳ Still running... (https://github.com/ansys/my-repo/actions/runs/1234567890)
[build.yml] ⏳ Still running... (https://github.com/ansys/my-repo/actions/runs/1234567890)
[build.yml] ✅
