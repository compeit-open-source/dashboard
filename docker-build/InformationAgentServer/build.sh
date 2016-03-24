#!/bin/sh

cd ../../component_adaptations/InformationAgentServer/
tar cvfz ../../docker-build/InformationAgentServer/ias.tar.gz *
cd ../../docker-build/InformationAgentServer/

docker build -t test/ias .
