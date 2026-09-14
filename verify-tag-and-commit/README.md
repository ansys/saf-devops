# 🏷️ Verify Tag and Commit

This GitHub Action verifies whether a specified tag exists and checks if the current commit is already tagged with that tag.


## 🔧 Inputs

### ✅ Required

| Input | Description | Example |
|-------|-------------|---------|
| `tag` | 🏷️ Tag name to verify | `v1.0.0` |

### ⚙️ Optional

| Input | Description | Default |
|-------|-------------|---------|
| `raise-error-on-untagged-commit` | ❌ Fail the action if the current commit is not tagged with the specified tag | `false` |

## 📤 Outputs

| Output | Description | Values |
|--------|-------------|--------|
| `tag-exists` | 🔍 Whether the specified tag exists in the repository | `true` or `false` |
| `commit-is-already-tagged` | 🔗 Whether the current commit is tagged with the specified tag | `true` or `false` |

## 🚀 Usage

### 🎯 Basic Example

```yaml
- name: Verify tag status
  id: verify
  uses: ansys/saf-devops/verify-tag-and-commit@v1
  with:
    tag: 'v1.0.0'

- name: Check results
  run: |
    echo "Tag exists: ${{ steps.verify.outputs.tag-exists }}"
    echo "Commit tagged: ${{ steps.verify.outputs.commit-is-already-tagged }}"
```

### 🔧 Advanced Example with Conditional Logic

```yaml
jobs:
  verify-and-tag:
    runs-on: ubuntu-latest
    steps:
      - name: Verify tag and commit
        id: verify
        uses: ansys/saf-devops/verify-tag-and-commit@v1
        with:
          tag: 'v1.0.0'

      - name: Create tag if it doesn't exist
        if: steps.verify.outputs.tag-exists == 'false'
        run: |
          git tag v1.0.0
          git push origin v1.0.0
          echo "✅ Tag created successfully"

      - name: Skip if already tagged
        if: steps.verify.outputs.commit-is-already-tagged == 'true'
        run: echo "⏭️ Commit already tagged - skipping"
```

### 🚨 Example with Error Enforcement

```yaml
- name: Ensure commit is properly tagged
  uses: ansys/saf-devops/verify-tag-and-commit@v1
  with:
    tag: ${{ github.ref_name }}
    raise-error-on-untagged-commit: 'true'
```

## 🔍 How It Works

The action performs the following steps:

1. **📥 Checkout**: Fetches the repository with full git history (`fetch-depth: 0`)
2. **🔍 Tag Check**: Uses `mukunku/tag-exists-action` to determine if the specified tag exists
3. **📊 Commit Comparison**: Compares the current commit SHA with the commit that the tag points to
4. **📤 Output Generation**: Sets boolean outputs for downstream workflow decisions
5. **⚠️ Error Handling**: Optionally fails the workflow if conditions aren't met

## ⚠️ Important Notes

- **Git History Required**: The action requires full git history to compare commits accurately
- **Case Sensitive**: Tag names are case-sensitive
- **Remote Tags**: The action checks for tags in the remote repository
- **Shallow Clones**: Won't work correctly with shallow git clones due to incomplete history

## 🚨 Error Handling

When `raise-error-on-untagged-commit` is set to `true`, the action will fail if:
- ❗ The tag exists but points to a different commit than the current one
- ⚠️ The current commit is not tagged with the specified tag


## 🐛 Troubleshooting

### Common Issues

1. **"Tag not found" but tag exists**
   - Check tag name for typos or case sensitivity

2. **Action fails unexpectedly**
   - Verify the repository has proper git history
   - Check that the tag follows standard naming conventions

3. **Outputs are unexpected**
   - Remember that output names use hyphens: `tag-exists`, `commit-is-already-tagged`
   - Ensure you're referencing the correct step ID in downstream jobs
