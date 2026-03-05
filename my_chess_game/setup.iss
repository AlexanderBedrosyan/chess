; Inno Setup script – Chess Trainer
; Produces a single Setup_ChessTrainer.exe installer
; Download Inno Setup free: https://jrsoftware.org/isinfo.php

#define AppName      "Chess Trainer"
#define AppVersion   "1.0"
#define AppPublisher "Chess Trainer Project"
#define AppExeName   "ChessTrainer.exe"
#define SourceDir    "dist\ChessTrainer"

[Setup]
AppId={{A3F2C1B0-9E4D-4F72-8C1A-D5E6F7A8B9C0}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL=https://github.com
AppSupportURL=https://github.com
AppUpdatesURL=https://github.com
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Single compressed installer file
OutputDir=installer
OutputBaseFilename=Setup_ChessTrainer
Compression=lzma2/ultra64
SolidCompression=yes
; Require 64-bit Windows
ArchitecturesInstallIn64BitMode=x64
; Show a nice wizard
WizardStyle=modern
; Desktop and Start Menu shortcuts
SetupIconFile=pieces\chess-logo.ico
UninstallDisplayIcon={app}\{#AppExeName}
; Minimum Windows 10
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Copy every file from the PyInstaller output folder
Source: "{#SourceDir}\{#AppExeName}";   DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\_internal\*";     DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";  Filename: "{uninstallexe}"
; Desktop (optional)
Name: "{autodesktop}\{#AppName}";      Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
