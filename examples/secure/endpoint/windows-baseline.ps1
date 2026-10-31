# TSAR reference: Windows endpoint baseline
# Apply via Group Policy or Intune.

# BitLocker with XTS-AES-256, TPM + PIN
Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 `
    -UsedSpaceOnly -TpmProtector -PinProtector `
    -RecoveryPasswordProtector

# Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -DisableBehaviorMonitoring $false
Set-MpPreference -DisableIOAVProtection $false
Set-MpPreference -MAPSReporting Advanced
Set-MpPreference -SubmitSamplesConsent SendSafeSamples
Set-MpPreference -CloudBlockLevel High

# Attack Surface Reduction
Add-MpPreference -AttackSurfaceReductionRules_Ids `
    BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550 `
    -AttackSurfaceReductionRules_Actions Enabled
Add-MpPreference -AttackSurfaceReductionRules_Ids `
    D4F940AB-401B-4EFC-AADC-AD5F3C50688A `
    -AttackSurfaceReductionRules_Actions Enabled
Add-MpPreference -AttackSurfaceReductionRules_Ids `
    3B576869-A4EC-4529-8536-B80A7769E899 `
    -AttackSurfaceReductionRules_Actions Enabled

# Windows Update
Set-Service -Name wuauserv -StartupType Automatic
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" `
    -Name "NoAutoUpdate" -Value 0
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" `
    -Name "AUOptions" -Value 4

# SMBv1 disabled
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# PowerShell logging
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
    -Name "EnableScriptBlockLogging" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" `
    -Name "EnableModuleLogging" -Value 1

# Credential Guard
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\LSA" `
    -Name "LsaCfgFlags" -Value 1

# Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow

# Screen lock policy
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" `
    -Name "InactivityTimeoutSecs" -Value 900
