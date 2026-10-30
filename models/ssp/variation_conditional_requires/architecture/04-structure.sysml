package VariationConditionalRequires {
  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation part def GainChoice {
    in port u : RealSignal;
    out port y : RealSignal;
    variant part singleStage : Gain;
    variant part twoStages : CascadedGain;
  }

  /* A condition over two variation points. The adapter captures and evaluates it;
   * build.py asks the adapter and rejects the illegal branch. */
  constraint def SineRequiresSingleStage {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenGain == GainChoice::singleStage
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : GainChoice;
    connect source.y to gain.u;

    constraint requiresSingleStage : SineRequiresSingleStage {
      in chosenSource = source;
      in chosenGain = gain;
    }
    assert requiresSingleStage;
  }

  /* Configurations: each binds both structural points; the constraint is
     inherited from System and evaluated at the composed path. */
  part def StepSingleSystem :> System {
    part :>> source = SourceChoice::stepImplementation;
    part :>> gain = GainChoice::singleStage;
  }

  part def StepTwoSystem :> System {
    part :>> source = SourceChoice::stepImplementation;
    part :>> gain = GainChoice::twoStages;
  }

  part def SineSingleSystem :> System {
    part :>> source = SourceChoice::sineImplementation;
    part :>> gain = GainChoice::singleStage;
  }

  part def SineTwoSystem :> System {
    part :>> source = SourceChoice::sineImplementation;
    part :>> gain = GainChoice::twoStages;
  }
}
