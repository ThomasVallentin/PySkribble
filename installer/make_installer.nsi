; example1.nsi
;
; This script is perhaps one of the simplest NSIs you can make. All of the
; optional settings are left to their default settings. The installer simply 
; prompts the user asking them where to install, and drops a copy of example1.nsi
; there. 
!include MUI2.nsh
!include FileFunc.nsh

;--------------------------------
;Perform Machine-level install, if possible

!define MULTIUSER_EXECUTIONLEVEL Highest
;Add support for command-line args that let uninstaller know whether to
;uninstall machine- or user installation:
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!include MultiUser.nsh
!include LogicLib.nsh

;--------------------------------

; The name of the installer
Name BetterSkribble

; The file to write
OutFile BetterSkribbleInstaller.exe

; The default installation directory
InstallDir "$PROGRAMFILES"

; Settings
!define MUI_ABORTWARNING


;--------------------------------
;Pages

    !define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of BetterSkribble.$\r$\n$\r$\n$\r$\nClick Next to continue."
    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_DIRECTORY
    !insertmacro MUI_PAGE_INSTFILES
        !define MUI_FINISHPAGE_NOAUTOCLOSE
        !define MUI_FINISHPAGE_RUN
        !define MUI_FINISHPAGE_RUN_UNCHECKED
        !define MUI_FINISHPAGE_RUN_TEXT "Run BetterSkribble"
        !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
    !insertmacro MUI_PAGE_FINISH

    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer

!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\BetterSkribble"
Section
  ;Add a folder to the hierarchy
  StrCpy $INSTDIR $INSTDIR\BetterSkribble

  CreateDirectory $INSTDIR
  SetOutPath $INSTDIR

  File /r ".\dist\BetterSkribble\*"

  WriteRegStr SHCTX "Software\BetterSkribble" "" $INSTDIR
  WriteUninstaller "$INSTDIR\uninstall.exe"
  CreateShortCut "$SMPROGRAMS\BetterSkribble.lnk" "$INSTDIR\BetterSkribble.exe"
  WriteRegStr SHCTX "${UNINST_KEY}" "DisplayName" "BetterSkribble"
  WriteRegStr SHCTX "${UNINST_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode"
  WriteRegStr SHCTX "${UNINST_KEY}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode /S"
  WriteRegStr SHCTX "${UNINST_KEY}" "Publisher" "Thomas Vallentin"
  WriteRegDWORD SHCTX "${UNINST_KEY}" "EstimatedSize" "100000"

SectionEnd

Function LaunchLink
  !addplugindir "."
  ShellExecAsUser::ShellExecAsUser "open" "$INSTDIR\BetterSkribble\BetterSkribble.exe"
FunctionEnd

;--------------------------------
; Uninstaller

Section "Uninstall"

  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\BetterSkribble.lnk"
  DeleteRegKey /ifempty SHCTX "Software\BetterSkribble"
  DeleteRegKey SHCTX "${UNINST_KEY}"

SectionEnd