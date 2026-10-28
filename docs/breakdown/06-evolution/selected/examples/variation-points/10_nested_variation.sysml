/* Example 10 -- nested variation: one dotted selection resolves two points.
 *
 * Pattern: the composition is fixed around one outer variation point, and the
 * selected body of that point carries an inner variation point of its own.
 * The direct path is a single gain stage. The nested path puts one processing
 * stage in front of the same gain, and that stage is itself a choice between
 * two FMUs. One selection therefore names both levels:
 *
 *     path=nestedPath  path.stage=attenuateStage
 *
 * The outer key names the part usage "path" in System; the inner key extends
 * it with "stage", the variation usage that only exists inside the selected
 * body. The dot is the whole binding mechanism: selection stays outside SysML
 * and is applied outermost first, so the inner point is looked up after the
 * outer body has been synthesized.
 *
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership) for both points. The body form is the same as example 08:
 * VariantUsageMember is "variant" followed by VariantUsageElement, whose
 * PartUsage alternative reaches Usage -> UsageCompletion -> UsageBody ->
 * DefinitionBody, and DefinitionBody admits further PartUsage members and
 * VariantUsageElementContext nodes. The inner usage writes its own "variation"
 * prefix and its own variant members; the pinned parser drops both, so the
 * adapter recovers them from the raw tree, exactly as it does for the outer
 * members. Grammar source: Systems-Modeling/SysML-v2-Pilot-Implementation,
 * org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext, rules
 * VariantUsageMember, VariantUsageElement, PartUsage, Usage, UsageBody,
 * DefinitionBody and PartDefinition. Only two levels are supported; a third
 * level is rejected with an explicit error rather than flattened.
 *
 * Expected SSP/FMI mapping: selecting path=nestedPath synthesizes
 * PathChoice__nestedPath for the "path" usage, so SystemStructure.ssd carries a
 * "path" subsystem in every case. With path.stage=gainStage that subsystem has
 * two <Part> entries, stage -> Gain.fmu and gain -> Gain.fmu, and three
 * connections: u to stage.u, stage.y to gain.u, gain.y to y. With
 * path.stage=attenuateStage the component tree is identical and only stage's
 * source becomes Attenuate.fmu; the outer System keeps source.y to path.u and
 * path.y to the system output in both. Selecting only path=nestedPath leaves
 * the inner point unselected and the build errors naming "path.stage", never
 * an empty or partial subsystem.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors. The
 * parsed model drops the whole inner variation usage together with its
 * variants, and drops every variant member of the outer point. The adapter
 * recovers the outer bodies, the inner usage, and the inner variants from the
 * raw parse tree. A selection that names path.stage without selecting path
 * first fails as an unknown key: the inner usage has no host until the outer
 * body is chosen.
 */
package NestedVariation {
  part def SspModel;

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
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

  attribute def AttenuateFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/attenuate";
    attribute implementation = "CoSimulation";
  }

  part def Step {
    attribute fmu_meta : StepFmu;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def Attenuate {
    attribute fmu_meta : AttenuateFmu;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  /* Inner point: the stage that feeds the gain in the nested path. */
  variation part def StageChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part gainStage : Gain;
    variant part attenuateStage : Attenuate;
  }

  /* Outer point. Its direct body holds no variation; its nested body does. */
  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part directPath {
      part gain : Gain;
      connect u to gain.u;
      connect gain.y to y;
    }

    variant part nestedPath {
      /* The inner usage declares the same alternatives as its definition. */
      variation part stage : StageChoice {
        variant part gainStage : Gain;
        variant part attenuateStage : Attenuate;
      }

      part gain : Gain;
      connect u to stage.u;
      connect stage.y to gain.u;
      connect gain.y to y;
    }
  }

  part def System :> SspModel {
    out port y : RealSignal;
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Step;
    part path : PathChoice;

    /* Fixed in every selection: only the outer point's ports are named. */
    connect source.y to path.u;
    connect path.y to y;
  }
}
