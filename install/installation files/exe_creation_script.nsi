Name "desktop kirby installer"
OutFile "desktop kirby installer.exe"

InstallDir "$PROGRAMFILES\desktop kirby\"

Section

SetOutPath $INSTDIR

File /r "C:\Users\noahm\Desktop\desktop-kirby\*"

CreateShortcut "$SMPROGRAMS\Startup\poyo.lnk" "$INSTDIR\poyo.exe"
CreateShortcut "$SMPROGRAMS\poyo.lnk" "$INSTDIR\poyo.exe"

SectionEnd