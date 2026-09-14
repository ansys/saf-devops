# ©2024, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

param ($extra, $placeholders)

# Usage (run from solution root)
# .\build\apply_mustache_templates.ps1 -extra "{sha: '1234'}" -placeholders ".github\\workflows\\placeholders.json"

# Force install the module we need, skip the confirmation prompt
Install-Module Poshstache -Confirm:$false -Force

Write-Output "Input JSON: $extra"

# Gather the data
$jsonContent = Get-Content $placeholders
$jsonData = $jsonContent | ConvertFrom-Json
$extraJson = $extra | ConvertFrom-Json

# Combine input placeholders with static placeholders from file
foreach ($obj in $extraJson.psobject.properties) {
    $jsonData | Add-Member -Name $obj.Name -Value $obj.Value -MemberType "NoteProperty"
}

# Convert back into what we need for poshstache
$jsonConfig = $jsonData | ConvertTo-Json | Out-String

# Some debug output in case we are lost
Write-Host "Final JSON data: $jsonConfig"
$currentDirectory = (Get-Item .).FullName
Write-Host "Current directory: $currentDirectory"

# Apply the placeholders to all files defined (in-place overwrite)
foreach ($file in $jsonData.files) {
    Write-Host "Applying template $placeholders to file: $file"

    # 2 step process because we can't overwrite the file while poshstache is using it
    $result = ConvertTo-PoshstacheTemplate -InputFile "$file" -ParametersObject $jsonConfig
    $result | Out-File "$file" -Force -Encoding "UTF8"
}
