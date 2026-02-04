[Setup]
AppId={{6E440B70-A511-468B-AE6F-06B42177E4E0}}
AppName=TimeTickIt
AppVersion=1.0.0
AppPublisher=CARLO_CABASE
DefaultDirName={localappdata}\Programs\TimeTickIt
DefaultGroupName=TimeTickIt
UninstallDisplayIcon={app}\TimeTickIt.exe
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

OutputDir=release
OutputBaseFilename=TimeTickItSetup

[Files]
Source: "dist\TimeTickIt\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Icons]
Name: "{group}\TimeTickIt"; Filename: "{app}\TimeTickIt.exe"
Name: "{userdesktop}\TimeTickIt"; Filename: "{app}\TimeTickIt.exe"; Tasks: desktopicon