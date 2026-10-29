package Embrace {
  part def SspModel;
  part def Analysis;

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.01;
  }

  attribute def SspMetadata {
    attribute source : String;
  }

  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/embrace/ssp";
  }

  part def EmbraceModel :> SspModel {
    attribute ssp_meta : LegacySsp;
  }

  part def baseline :> Analysis {
    doc /* Legacy embrace SSP body over the baseline experiment window. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : EmbraceModel;
  }
}
