package VariationConditionalExcludes {
  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation attribute def ScenarioChoice {
    variant attribute baseline : BaselineScenario;
    variant attribute highGain : HighGainScenario;
  }

  /* A condition that crosses from a structural point to an attribute point.
   * The adapter captures and evaluates it; build.py asks the adapter. */
  constraint def SineExcludesHighGain {
    in chosenSource : SourceChoice;
    in chosenScenario : ScenarioChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenScenario != ScenarioChoice::highGain
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : Gain;
    connect source.y to gain.u;
  }

  /* Configurations: each binds the source point. The scenario point is local
     to the analysis, which carries its own feature value. */
  part def StepSystem :> System {
    part :>> source = SourceChoice::stepImplementation;
  }

  part def SineSystem :> System {
    part :>> source = SourceChoice::sineImplementation;
  }
}
