/* Example 07 -- an explicit selection element. PROPOSAL, NOT A STANDARD SHAPE.
 *
 * Pattern: the architecture of example 05 carries a fourth part, "selection",
 * whose attributes name the chosen variant at each of the three variation
 * points. That part is the only place where a selection is written down, so one
 * SSP build reads it and no other element has to change between selections.
 *
 * This shape is a proposal. SysML 2.0 has no selection element, no
 * configuration element and no binding-time mechanism: nothing in the language
 * says when a variant is chosen, by what, or that a choice ever happens. What
 * the specification does say is in the Variability part of section 7.6.1: a
 * configuration "is selected by selecting a variant for each variation", and
 * "Variability modeling in SysML can augment other external variability modeling
 * applications, which provide robust capabilities for managing variability
 * across multiple kinds of models ... and auto-generating the variant design
 * configurations based on the selections". The alignment note that follows puts
 * that external role next to ISO/IEC 26580:2021, whose PLE factory configurator
 * (26580 3.12) produces product asset instances from a bill-of-features.
 * So the standard delegates selection to an external variability tool and this
 * file stands in for that tool with a typed record inside the model.
 *
 * Why attributes and not references: an attribute cannot be typed by a part
 * definition, and a variant is a part usage, so the record cannot point at the
 * selected variant directly. It names it with a String, and the build tool
 * matches the string against the variant names. Nothing checks that match: a
 * typo produces a different error, not a model error. The one legality rule in
 * this file is asserted over strings, which shows the weakness of the proposal
 * rather than hiding it; example 06 shows the same rule over variation usages,
 * where the language can check it.
 *
 * Vocabulary: the record is a selection of one variant per variation point in
 * the ISO/IEC 26550:2015 3.28 / 3.29 sense. It is not a 3.24 variability
 * constraint and not a 3.25 variability dependency. In 26580:2021 terms it is a
 * degenerate bill-of-features (3.1): features were never modelled, so the record
 * names assets directly. A real 26580 flow would put the record in a feature
 * catalogue and let the configurator drive the asset variation points.
 *
 * Standard anchor: section 7.6.7 for the variation points, section 7.6.1
 * (Variability) for the delegation to external tooling, and section 7.20 for
 * the constraint. The selection element itself has no anchor.
 *
 * Expected SSP/FMI mapping: one Selection part becomes one build invocation, so
 * the artifact set is exactly example 05's: one SSD, one SSV per scenario, one
 * SSM. The selection record itself does not cross into the SSP at all; if the
 * provenance has to name the selection, the build tool has to write it outside
 * the standard artifacts.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors; the
 * selection part definition and its String attributes are ordinary SysML. The
 * adapter then rejects the composition while validating parameter attributes:
 * "Selection.selectedSource is a flat parameter attribute, which is no longer
 * supported. Declare a parameter interface with 'in port parameters :
 * <Interface>;' and apply a ParameterSet with 'bind'." (parameters.py, the flat
 * parameter check). The standard syntax is kept as written and the rejection is
 * recorded here, because it is the finding: the adapter reads any plain
 * attribute of a part used in a composition as a parameter, so a selection
 * record cannot ride in the architecture unless it is declared as a parameter
 * interface -- which is the parameter mechanism, not a selection mechanism.
 */
package SelectionConfiguration {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def SineParameters :> ParameterInterface {
    attribute amplitude : Real;
    attribute f : Real;
    attribute offset : Real;
    attribute phase : Real;
    attribute startTime : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def ParameterSet;

  attribute def BaselineScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 3.0;
  }

  attribute def LateStepScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.75;
    attribute k = 3.0;
  }

  attribute def HighGainScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 9.0;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
    attribute tolerance : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
    attribute tolerance = 0.0001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def StepFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Step/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def SignalSource {
    out port y : RealSignal;
  }

  part def Step :> SignalSource {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port :>> y : RealSignal;
  }

  part def Sine :> SignalSource {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port :>> y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
  }

  part def CascadedGain {
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
    part firstStage : Gain;
    part secondStage : Gain;
    connect u to firstStage.u;
    connect firstStage.y to secondStage.u;
    connect secondStage.y to y;
    connect parameters to firstStage.parameters;
    connect parameters to secondStage.parameters;
  }

  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation part def GainChoice {
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
    variant part singleStage : Gain;
    variant part twoStages : CascadedGain;
  }

  variation attribute def ScenarioChoice {
    variant attribute baseline : BaselineScenario;
    variant attribute lateStep : LateStepScenario;
    variant attribute highGain : HighGainScenario;
  }

  /* The proposed selection element: one String per variation point. */
  part def Selection {
    doc /* Names one variant per variation point; read by the build tool. */
    attribute selectedSource : String = "stepImplementation";
    attribute selectedGain : String = "singleStage";
    attribute selectedScenario : String = "baseline";
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : GainChoice;
    part selection : Selection;
    connect source.y to gain.u;

    /* The rule of example 06, carried over the recorded strings. */
    assert constraint recordedSelectionIsLegal {
      selection.selectedSource != "sineImplementation" or
        selection.selectedGain == "singleStage"
    }
  }

  part def test_selected :> Study {
    doc /* The study does not choose; the build tool reads the record. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
