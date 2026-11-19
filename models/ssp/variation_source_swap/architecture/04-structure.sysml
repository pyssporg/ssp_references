package VariationSourceSwap {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def VariationSourceSwapDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  /* One variation point: the source stage is one of two FMU implementations. */
  variation part def SourceChoice {
    out port y : RealSignal;

    variant part step : Step;
    variant part sine : Sine;
  }

  part def System :> SspModel {
    attribute defaults : VariationSourceSwapDefaultExperiment;

    part source : SourceChoice;

  }

  /* Configurations: each binds the source point to one variant. */
  part def StepSystem :> System {
    part :>> source = SourceChoice::step;
  }

  part def SineSystem :> System {
    part :>> source = SourceChoice::sine;
  }
}
