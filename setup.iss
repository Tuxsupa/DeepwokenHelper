#define MyAppName "Deepwoken Helper"
#define MyAppVersion "1.3.1"
#define MyAppPublisher "Tuxsuper"
#define MyAppURL "https://github.com/Tuxsupa/DeepwokenHelper"
#define MyAppExeName "Deepwoken Helper.exe"
#define SourceRoot "E:\Coding\DeepwokenHelper"


[Setup]
AppId={{1326559D-EBCC-4C62-B809-9EB6AABF3CAB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile={#SourceRoot}\LICENSE.txt
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
OutputDir={#SourceRoot}\setups
OutputBaseFilename=DeepwokenHelper_Setup_{#MyAppVersion}
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile={#SourceRoot}\assets\icons\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
AlwaysShowDirOnReadyPage=yes
DisableDirPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceRoot}\dist\Deepwoken Helper\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceRoot}\dist\Deepwoken Helper\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceRoot}\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceRoot}\tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\assets"
Type: filesandordirs; Name: "{app}\yolov5"

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\DeepwokenHelper"
Type: filesandordirs; Name: "{localappdata}\DeepwokenHelper"