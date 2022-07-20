#!/bin/bash
set -e -x

arm64_set_path_and_python_version(){
  python_version="$1"
  if [[ $(/usr/bin/arch) = arm64 ]]; then
      export PATH=/opt/homebrew/bin:$PATH
      eval "$(pyenv init --path)"
      pyenv install $python_version -s
      pyenv global $python_version
      export PATH=$(pyenv prefix)/bin:$PATH
  fi
}