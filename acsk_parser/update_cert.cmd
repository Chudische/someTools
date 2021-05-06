@echo off
setlocal enabledelayedexpansion
copy /Y "Z:\cert\*.*" "C:\My Certificates and CRLs 13\"
set time=60
:loop
if NOT exist Z:\\cert (
%SystemRoot%\Sysnative\msg.exe %username% DISK Z: IS LOST!
timeout /t 300 /nobreak
goto loop
)

FC /a "Z:\cert\last.txt" "C:\My Certificates and CRLs 13\last.txt"
if errorlevel 1 (
type Z:\\cert\last.txt
set /p time=<Z:\\cert\last.txt
copy /Y "Z:\cert\*.*" "C:\My Certificates and CRLs 13\"
)
 
timeout /t !time! /nobreak
goto loop