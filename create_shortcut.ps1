$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\BF Estimator.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\run_bf_estimator.bat"
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.IconLocation = "C:\Windows\System32\SHELL32.dll,44"  # Using a calculator-like icon from Windows
$Shortcut.Save()
