package VariationAttributeSet {
  /* One attribute variation point: both variants fix the same parameter set. */
  variation attribute def ScenarioChoice {
    variant attribute nominalK3 : NominalK3;
    variant attribute boostedK9 : BoostedK9;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }
}
