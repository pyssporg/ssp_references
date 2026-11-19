package VanDerPol {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def VanDerPolDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 20.0;
  }

  port def VanDerPolParameters :> ParameterInterface {
    attribute mu : Real;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def FastScenario :> ParameterSet {
    attribute mu = 2.0;
  }

  attribute def SlowScenario :> ParameterSet {
    attribute mu = 0.5;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 20.0;
    attribute stepSize = 0.001;
  }

  attribute def FastExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def SlowExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 20.0;
    attribute stepSize = 0.001;
  }

  attribute def VanDerPolFmu :> FmuMetadata {
    attribute source = "models/fmu/VanDerPol/fmu";
    attribute implementation = "CoSimulation";
  }

  part def VanDerPol {
    attribute fmu_meta : VanDerPolFmu;
    in port parameters : VanDerPolParameters;
    out port x0 : RealSignal;
    out port x1 : RealSignal;
  }

  part def System :> SspModel {
    attribute defaults : VanDerPolDefaultExperiment;

    part fmu : VanDerPol;
  }

  part def baseline :> Analysis {
    doc /* Baseline configuration with mu set to 1.0. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }

  part def fast :> Analysis {
    doc /* Variant configuration with mu set to 2.0. */
    attribute experiment_fast : FastExperiment;
    attribute scenario : FastScenario;
    part sut : System;

    bind sut.fmu.parameters.mu = scenario.mu;
  }

  part def slow :> Analysis {
    doc /* Variant configuration with mu set to 0.5. */
    attribute experiment_slow : SlowExperiment;
    attribute scenario : SlowScenario;
    part sut : System;

    bind sut.fmu.parameters.mu = scenario.mu;
  }
}
