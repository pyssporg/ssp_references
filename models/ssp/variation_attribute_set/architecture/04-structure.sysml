package VariationAttributeSet {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def VariationAttributeSetDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  /* One attribute variation point: both variants fix the same parameter set. */
  variation attribute def ScenarioChoice {
    variant attribute nominalK3 : NominalK3;
    variant attribute boostedK9 : BoostedK9;
  }

  part def System :> SspModel {
    attribute defaults : VariationAttributeSetDefaultExperiment;

    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }
}
