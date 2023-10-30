#!/bin/bash
#cd htcondorce_on_vagrant
htcondorce_on_vagrant/00_install_role.sh

ansible-playbook 01_hosts.yml
ansible-playbook 02_epel.yml
ansible-playbook 06_htcondor.yml

