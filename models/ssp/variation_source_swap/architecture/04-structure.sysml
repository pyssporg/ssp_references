package VariationSourceSwap {
  /* One variation point: the source stage is one of two FMU implementations. */
  variation part def SourceChoice {
    out port y : RealSignal;

    variant part step : Step;
    variant part sine : Sine;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
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
