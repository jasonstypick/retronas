#!/bin/bash

touch $HOME/.gitconfig
git config list --global | grep -E "safe\.directory=*" &>/dev/null
if [ $? -eq 1 ] 
then
  git config --global --add safe.directory '*'
fi
