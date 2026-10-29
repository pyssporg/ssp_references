/* Example 08 -- connection variation: the wiring, not just the type, differs.
 *
 * Pattern: one composition with a fixed source and a fixed outer wiring, whose
 * signal path is a variation point. The direct path is a single gain stage; the
 * filtered path is two gain stages in series. The variation definition declares
 * three ports (u, y, parameters), and both variant bodies wire themselves
 * between those same three names, so the outer composition and its two
 * connections are identical in every selection. What
 * differs is what happens between u and y: one part and three connects against
 * two parts and five connects.
 *
 * SysML 2.0 has no variant "connect" that can carry this choice. "connect" is
 * a connection usage, and the reference grammar does list ConnectionUsage among
 * the VariantUsageElement alternatives, so "variant connect a.y to b.u;" is
 * writable; but a connection only relates parts that already exist. Selecting
 * a connection variant cannot add or remove a part, and it would be a second
 * variation point over connectors, not a choice between two decompositions.
 * Because the direct and filtered selections differ in part count, the choice
 * has to sit on a part. The variation point therefore cannot be placed on the
 * outer "connect source.y to path.u": the choice is expressed by giving each
 * variant usage its own body with its own nested parts and its own connects.
 * The outer connects then touch only the variation definition's ports, which
 * both variant bodies use and neither redefines, so they are the same in every
 * selection.
 *
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership) for the point itself. The body form is confirmed by the
 * grammar: VariantUsageMember is "variant" followed by VariantUsageElement,
 * whose PartUsage alternative is OccurrenceUsagePrefix "part" Usage; Usage is
 * UsageDeclaration? UsageCompletion, UsageCompletion is ValuePart? UsageBody and
 * UsageBody is DefinitionBody. The usage declaration is optional, so
 * "variant part name { ... }" is legal, and the body is the implicit anonymous
 * definition of that part usage. DefinitionBody admits OccurrenceUsageMember
 * and NonOccurrenceUsageMember, which is where the nested parts, the connects
 * (ConnectionUsage) and the binds (BindingConnectorAsUsage) come from.
 * Grammar source: Systems-Modeling/SysML-v2-Pilot-Implementation,
 * org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext, rules
 * VariantUsageMember, VariantUsageElement, PartUsage, Usage, UsageBody and
 * DefinitionBody. Connect and binding usages are the section 7.12 subject in
 * the specification.
 *
 * Expected SSP/FMI mapping: one selection yields one SSP. The selected body
 * becomes an anonymous definition for the "path" usage, so "path" is emitted
 * as an <ssd:System>, not as a flattened part list. The direct selection gives
 * a path subsystem with one <Part> (gain) and two <ssd:Connection> entries:
 * u to gain.u and gain.y to y. The filtered selection gives a path subsystem
 * with two <Part> entries (firstStage, gain) and three connections: u to
 * firstStage.u, firstStage.y to gain.u, and gain.y to y. The outer composition
 * is identical in both: source.y to path.u and path.y to the system output.
 * The two artifacts therefore differ inside one subsystem, in element count and
 * connector names, not merely in a type or a value; a comparison case built for
 * one selection cannot be reused for the other without regenerating the SSD.
 * The parameter connects inside each variant are captured on the variant body
 * but are not emitted as SSD connections: SSP applies parameters with binds and
 * an SSM, and this file applies no set inside the variant, so no mapping is
 * generated for them.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors but the
 * parsed model drops both variant usages, including their nested parts and
 * connects. The adapter recovers each variant body from the raw parse tree.
 * Selecting "path=directPath" or "path=filteredPath" retypes the path usage to
 * a synthesized definition (PathChoice__directPath or PathChoice__filteredPath)
 * that carries PathChoice's ports, and generation writes the subsystems above.
 * Without a selection the build is rejected as unselected.
 */
package ConnectionVariation {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
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

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Step {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
  }

  /* The variation point. Its ports are the contract every variant has to wire,
   * because the outer composition connects to these and to nothing else. */
  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;

    /* Direct path: one stage, so the outer source reaches the gain directly. */
    variant part directPath {
      part gain : Gain;
      connect u to gain.u;
      connect gain.y to y;
      connect parameters to gain.parameters;
    }

    /* Filtered path: the same endpoints, one more stage in between. */
    variant part filteredPath {
      part firstStage : Gain;
      part gain : Gain;
      connect u to firstStage.u;
      connect firstStage.y to gain.u;
      connect gain.y to y;
      connect parameters to firstStage.parameters;
      connect parameters to gain.parameters;
    }
  }

  part def System :> SspModel {
    out port y : RealSignal;
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Step;
    part path : PathChoice;

    /* Fixed in every selection: only the variation point's ports are named. */
    connect source.y to path.u;
    connect path.y to y;
  }

  part def test_selected :> Analysis {
    doc /* One analysis per selection; the selection itself is not recorded here. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : BaselineScenario;
    part sut : System;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.parameters.k = scenario.k;
  }
}
