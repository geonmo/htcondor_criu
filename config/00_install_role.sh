#!/bin/bash
sudo yum update -y
sudo yum update -y ansible


ansible-galaxy role install geerlingguy.repo-epel
ansible-galaxy role install geonmo.htcondor
ansible-galaxy role install geonmo.grid
ansible-galaxy role install geonmo.htcondor_ce

