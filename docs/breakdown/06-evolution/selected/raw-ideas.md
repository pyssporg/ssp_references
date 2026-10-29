---
id: IMP-100
type: imp
title: Raw Improvement Ideas
summary: Unscoped improvement ideas; route each through the change pipeline.
date: 2026-10-22
status: current
pb_exempt: true
---

# Raw Improvement Ideas

---

use pyssp standard to create all possible ssp and ssd
- avoid manual xml definitions in the xitures such as models/ssp/signal_nested_parameter_bindings/ssp/SystemStructure.ssd, models/ssp/signal_nested_external_bindings/ssp/SystemStructure.ssd


---

Iterate over the improvement candidates until all are completed

---


package ParameterPortDemo {
  // Marker is now a port def (one carrier, one marker name)
  port def ParameterInterface;

  port def AutopilotParameters :> ParameterInterface {
    attribute waypointCount : Integer;
    attribute waypointX_km : Real[3];
    attribute maxSpeed_kmh : Real = 120.0;        // interface default -> FMI start
  }

  attribute def ParameterSet;
  attribute def NominalSet :> ParameterSet {
    attribute waypointCount  = 10;
    attribute waypointX_km   = (0.0, 10.0, 20.0);
  }

  part def AutopilotModule {
    in port parameters : AutopilotParameters;        // parameters are always inputs
    attribute nominal : NominalSet;

    bind parameters.waypointCount = nominal.waypointCount;
    bind parameters.waypointX_km  = nominal.waypointX_km;
  }

  part def AnalysisComposition {
    part autopilot : AutopilotModule;
    attribute aggressive : AggressiveSet;
    bind autopilot.parameters.waypointCount = aggressive.waypointCount;
  }

}

---


// defining common attributes all fmus should have
attribute def FmuMetaData; {
  attribute source;             // file or extracted FMU dir
  attribute resource_name;       // name under resources/
}

attribute def AutopilotFmu :> FmuMetaData {
  attribute source = "build/fmus/AutopilotModule.fmu";  // file or extracted FMU dir
  attribute resource_name = "AutopilotModule.fmu";       // name under resources/
}

part def AutopilotModule {
  attribute fmu_meta : AutopilotFmu;
  in port parameters : AutopilotParameters;
}