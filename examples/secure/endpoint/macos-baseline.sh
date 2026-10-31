#!/bin/bash
# TSAR reference: macOS endpoint baseline

set -euo pipefail

# FileVault
if ! fdesetup status | grep -q "FileVault is On"; then
  echo "FileVault must be enabled manually: fdesetup enable"
  exit 1
fi

# Gatekeeper
sudo spctl --master-enable

# Firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsigned on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsignedapp on

# Automatic updates
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate CriticalUpdateInstall -bool true
sudo defaults write /Library/Preferences/com.apple.commerce AutoUpdate -bool true
sudo defaults write /Library/Preferences/com.apple.SoftwareUpdate ConfigDataInstall -bool true

# Screen lock
sudo defaults write /Library/Preferences/com.apple.screensaver askForPassword -int 1
sudo defaults write /Library/Preferences/com.apple.screensaver askForPasswordDelay -int 0
sudo defaults write /Library/Preferences/.GlobalPreferences com.apple.screensaver.idleTime -int 900

# Disable remote login and remote management
sudo systemsetup -setremotelogin off 2>/dev/null || true
sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -stop 2>/dev/null || true

# Audit logging
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.auditd.plist 2>/dev/null || true

# Password policy (12 chars, 1 hour lockout after 5 failures)
sudo pwpolicy setaccountpolicies /etc/security/pwpolicy.plist 2>/dev/null || true

echo "macOS baseline applied"
