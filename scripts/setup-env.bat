@echo off
REM =============================================================================
REM CLASH ROYALE DECK BUILDER - ENVIRONMENT SETUP SCRIPT (Windows)
REM =============================================================================
REM This script initializes environment files from the template for consistent
REM configuration across different environments.
REM =============================================================================

setlocal enabledelayedexpansion

REM Colors for output (Windows compatible)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Function to generate simple password (Windows compatible)
set "chars=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
set "password="
for /l %%i in (1,1,25) do (
    set /a "rand=!random! %% 62"
    for %%j in (!rand!) do set "password=!password!!chars:~%%j,1!"
)

REM Check if .env.example exists
if not exist ".env.example" (
    echo %ERROR% .env.example not found! Please ensure you're in the project root directory.
    exit /b 1
)

REM Create scripts directory if it doesn't exist
if not exist "scripts" mkdir scripts

echo %INFO% Starting environment setup for Clash Royale Deck Builder...

REM Function to setup environment file
:setup_env_file
set "env_file=%~1"
set "env_type=%~2"

if exist "%env_file%" (
    echo %WARNING% %env_file% already exists. Skipping creation.
    goto :eof
)

echo %INFO% Creating %env_file% for %env_type% environment...

REM Copy template
copy ".env.example" "%env_file%" >nul

REM Generate passwords
call :generate_password db_root_password
call :generate_password db_user_password
call :generate_password jwt_secret

REM Update environment-specific values using PowerShell for better text replacement
if "%env_type%"=="local" (
    powershell -Command "(Get-Content '%env_file%') -replace 'your_secure_root_password_here', 'local_root_%db_root_password%' -replace 'your_secure_user_password_here', 'local_user_%db_user_password%' -replace 'clash_deck_builder', 'clash_deck_builder_dev' -replace 'your_jwt_secret_key_here', '%jwt_secret%' -replace 'DEBUG=false', 'DEBUG=true' -replace 'LOG_LEVEL=info', 'LOG_LEVEL=debug' -replace 'ENVIRONMENT=production', 'ENVIRONMENT=development' -replace 'your_clash_royale_api_key_here', 'test_api_key_or_mock' | Set-Content '%env_file%'"
) else if "%env_type%"=="docker" (
    powershell -Command "(Get-Content '%env_file%') -replace 'your_secure_root_password_here', 'docker_root_%db_root_password%' -replace 'your_secure_user_password_here', 'docker_user_%db_user_password%' -replace 'clash_deck_builder', 'clash_deck_builder_docker' -replace 'your_jwt_secret_key_here', '%jwt_secret%' -replace 'DB_HOST=localhost', 'DB_HOST=database' -replace 'ENVIRONMENT=production', 'ENVIRONMENT=docker' | Set-Content '%env_file%'"
) else if "%env_type%"=="production" (
    powershell -Command "(Get-Content '%env_file%') -replace 'your_secure_root_password_here', 'prod_root_%db_root_password%' -replace 'your_secure_user_password_here', 'prod_user_%db_user_password%' -replace 'your_jwt_secret_key_here', '%jwt_secret%' | Set-Content '%env_file%'"
)

echo %SUCCESS% Created %env_file% with secure generated passwords
goto :eof

REM Function to generate password
:generate_password
set "result_var=%~1"
set "password="
for /l %%i in (1,1,25) do (
    set /a "rand=!random! %% 62"
    for %%j in (!rand!) do set "password=!password!!chars:~%%j,1!"
)
set "%result_var%=!password!"
goto :eof

REM Main execution
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

if "%1"=="all" (
    call :setup_env_file ".env.local" "local"
    call :setup_env_file ".env.docker" "docker"
    call :setup_env_file ".env" "production"
) else if "%1"=="local" (
    call :setup_env_file ".env.local" "local"
) else if "%1"=="docker" (
    call :setup_env_file ".env.docker" "docker"
) else if "%1"=="production" (
    call :setup_env_file ".env" "production"
) else (
    REM Default: create local and docker environments
    call :setup_env_file ".env.local" "local"
    call :setup_env_file ".env.docker" "docker"
)

echo.
echo %SUCCESS% Environment setup completed!
echo.
echo %WARNING% IMPORTANT SECURITY REMINDERS:
echo 1. Update the Clash Royale API key in your environment files
echo 2. For production, use strong, unique passwords
echo 3. Never commit .env files to version control
echo 4. Rotate passwords and API keys regularly
echo.
echo %INFO% Next steps:
echo 1. Update CLASH_ROYALE_API_KEY in your environment files
echo 2. Review and adjust other configuration values as needed
echo 3. Run 'docker-compose up' to start the application
goto :end

:show_help
echo Usage: %0 [environment]
echo.
echo Arguments:
echo   all         Create all environment files (.env.local, .env.docker, .env)
echo   local       Create only .env.local for local development
echo   docker      Create only .env.docker for containerized development
echo   production  Create only .env for production deployment
echo   (no args)   Create .env.local and .env.docker (default)
echo.
echo Examples:
echo   %0              # Create local and docker environments
echo   %0 all          # Create all environment files
echo   %0 production   # Create only production environment

:end
endlocal