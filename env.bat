@echo off
set arg=%1

:: A simple tool to work with virtual environments in python

:: Map argument to command name
if "%arg%" == "notebook" (
	set command=start
) else if "%arg%" == "nb" (
	set command=start
) else if "%arg%" == "run" (
	set command=start
) else if "%arg%" == "r" (
	set command=start
) else if "%arg%" == "u" (
	set command=update
) else if "%arg%" == "deactivate" (
	set command=stop
) else if "%arg%" == "d" (
	set command=stop
) else if "%arg%" == "leave" (
	set command=stop
) else if "%arg%" == "l" (
	set command=stop
) else if "%arg%" == "?" (
	set command=help
) else if "%arg%" == "h" (
	set command=help
) else (
	set command=%arg%
)

:: Display help if command is "help"
if "%command%" == "help" (
	echo [1;4mAvailable commands:[0m
	echo   [35menv [1mstart[0m   [1mstart[0m jupyter notebook[0m
	echo   [35menv [1mupdate[0m  [1mupdate[0m the project dependencies[0m
	echo   [35menv [1msetup[0m   [1msetup[0m the virtual environment[0m
	echo   [35menv [1mleave[0m   [1mleave[0m the virtual environment[0m
	echo   [35menv [1mhelp[0m    show this [1mhelp[0m
	exit /b 0
)

:: Setup the virtual environment if command is "setup" and it does not already exist
if not exist dsp_env\ (
	if "%command%" == "setup" (
		call python -m venv dsp_env
		call .\env.bat update
		exit /b 0
	) else (
		echo [1;41m Please run [101m'env setup'[0;41m. [0m
  		exit /b 1
	)
)


:: Activate the virtual environment
call .\dsp_env\Scripts\activate

:: Execute the right command
if "%command%" == "start" (
	call jupyter notebook
) else if "%command%" == "update" (
	call pip install -r requirements.txt
) else if "%command%" == "stop" (
	call deactivate
)