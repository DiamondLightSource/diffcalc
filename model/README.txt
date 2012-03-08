Setting up the sixc vrml model to work via Epics pv's from b16's simulation running on the office network.


1. Synoptic
$ launcher --port 6064

2. Shell
export EPICS_CA_REPEATER_PORT=6065
export EPICS_CA_SERVER_PORT=6064

3. Vrml viewer
export EPICS_CA_SERVER_PORT=6064
dls-vrml-epics-viewer.py fivec.wrl fivec.wcfg
