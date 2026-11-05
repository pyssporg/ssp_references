package DcMotor {
  private import PysspCore::*;

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/dcmotor/ssp";
  }

  part def DcMotorModel :> SspModel {
    attribute ssp_meta : LegacySsp;
  }

  part def baseline :> Analysis {
    doc /* Legacy dcmotor SSP body over the baseline experiment window. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : DcMotorModel;
  }
}
