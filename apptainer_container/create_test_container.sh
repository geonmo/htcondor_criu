#!/bin/bash
apptainer build ../criu.sif criu.def
apptainer build ../root.sif root.def
