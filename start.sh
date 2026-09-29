#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) platform=windows ;;
  Linux*) platform=linux ;;
  *) echo 'Sistema não suportado. Use Linux ou Git Bash no Windows.' >&2; exit 1 ;;
esac

if [[ "$platform" == windows ]]; then
  XAMPP_DIR="${XAMPP_DIR:-/c/xampp}"
  for script in apache_start.bat mysql_start.bat; do
    if [[ ! -f "$XAMPP_DIR/$script" ]]; then
      echo "Não encontrado: $XAMPP_DIR/$script. Configure XAMPP_DIR." >&2
      exit 1
    fi
  done
  export SETUP_XAMPP_DIR="$(cygpath -w "$XAMPP_DIR")"
  powershell.exe -NoProfile -Command '
    $ErrorActionPreference = "Stop"
    foreach ($service in @(@("httpd", "apache_start.bat"), @("mysqld", "mysql_start.bat"))) {
      if (-not (Get-Process -Name $service[0] -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath $env:ComSpec -ArgumentList @("/c", $service[1]) -WorkingDirectory $env:SETUP_XAMPP_DIR -WindowStyle Hidden
      }
    }
  '
else
  XAMPP_DIR="${XAMPP_DIR:-/opt/lampp}"
  if [[ ! -x "$XAMPP_DIR/lampp" ]]; then
    echo "Não encontrado: $XAMPP_DIR/lampp. Instale o XAMPP ou configure XAMPP_DIR." >&2
    exit 1
  fi
  if [[ "$EUID" -eq 0 ]]; then
    "$XAMPP_DIR/lampp" startapache
    "$XAMPP_DIR/lampp" startmysql
  else
    sudo "$XAMPP_DIR/lampp" startapache
    sudo "$XAMPP_DIR/lampp" startmysql
  fi
fi

if [[ -f venv/Scripts/activate ]]; then
  source venv/Scripts/activate
elif [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
else
  echo 'Ambiente virtual não encontrado. Execute bash setup.sh primeiro.' >&2
  exit 1
fi

exec fastapi dev main.py
