## status: correct
## teardown_command: rm -rf embrace1_res.mat
## linux: yes
## ucrt64: no
## win: no
## mac: no

from OMSimulator import SSP, Settings, CRef, Capi

Settings.suppressPath = True
Capi.setCommandLineOption("--wallTime=true --ignoreInitialUnknowns=false")

model = SSP('../resources/embrace.ssp')

instantiated_model = model.instantiate() 

## simulation settings
instantiated_model.setResultFile("oms_config1.csv")
instantiated_model.setStopTime(300.0)
instantiated_model.setFixedStepSize(1e-3)
instantiated_model.setLoggingInterval(1)

instantiated_model.initialize()
instantiated_model.simulate()
instantiated_model.terminate()
instantiated_model.delete()

