/* Example 03 -- model-level configuration with legality constraints.
 *
 * Standard anchor: SysML v2.0 Language §7.6.7 for the variation points, and
 * §7.20 for the constraint definitions, usages, and asserts.
 *
 * A configuration selects variants; it does not make the selection legal. The
 * constraint stays the same as in the string-based fixtures and is evaluated
 * against the derived selection map. An illegal configuration is authored on
 * purpose (`SineTwoSystem`) so the plan can report it as violated.
 *
 * Derived maps:
 *   StepSingleSystem   -> {"source": "stepImplementation", "gain": "singleStage"}
 *   StepTwoSystem      -> {"source": "stepImplementation", "gain": "twoStages"}
 *   SineSingleSystem   -> {"source": "sineImplementation", "gain": "singleStage"}
 *   SineTwoSystem      -> {"source": "sineImplementation", "gain": "twoStages"}
 *
 * The requires rule admits the first three and rejects the fourth.
 */
package ConditionalConfiguration {
  part def SspModel;
  part def Analysis;

  variation part def SourceChoice {
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation part def GainChoice {
    variant part singleStage : Gain;
    variant part twoStages : Gain;
  }

  part def Step;
  part def Sine;
  part def Gain;

  constraint def SineRequiresSingleStage {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenGain == GainChoice::singleStage
  }

  part def System :> SspModel {
    part source : SourceChoice;
    part gain : GainChoice;

    constraint requiresSingleStage : SineRequiresSingleStage {
      in chosenSource = source;
      in chosenGain = gain;
    }
    assert requiresSingleStage;
  }

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

  part def step_single :> Analysis {
    part sut : StepSingleSystem;
  }

  part def step_two :> Analysis {
    part sut : StepTwoSystem;
  }

  part def sine_single :> Analysis {
    part sut : SineSingleSystem;
  }

  part def sine_two :> Analysis {
    part sut : SineTwoSystem;
  }
}
