package DcMotor {
  part def SspModel;
  part def Study;

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def SspMetadata {
    attribute source : String;
  }

  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/dcmotor/ssp";
  }

  part def DcMotorModel :> SspModel {
    attribute ssp_meta : LegacySsp;
  }

  part def baseline :> Study {
    attribute experiment_baseline : BaselineExperiment;
    part sut : DcMotorModel;
  }
}
