/* Example 03 -- usage-level variation: the choice sits on a usage, not a definition.
 *
 * Pattern: the same two alternative sources as example 01, but the variation
 * point is declared on the part usage "source" inside the composition. The
 * variant members are usages that redefine "source" and are typed by existing
 * part definitions; no variation definition is introduced.
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership).
 *
 * Expected SSP/FMI mapping: the usage-level and definition-level forms produce
 * the same artifact, because SSP has no place to record where the choice was
 * declared. Exactly one variant becomes one <Part> of SystemStructure.ssd,
 * named after the variation usage ("source"), and typed by the selected FMU.
 * The name stays "source" in every selection, so the comparison gate and the
 * SSM mappings refer to it unchanged; only the component source differs.
 *
 * Pinned toolchain (sysmlpy 0.96.4): the parsed model has no variation flag
 * and no variant members, so the adapter recovers both from the raw parse
 * tree. Selecting "source=stepSource" or "source=sineSource" retypes the usage
 * on a copy and generation writes component "source" with resources/Step.fmu
 * or resources/Sine.fmu; without a selection the build is rejected as
 * unselected.
 */
package UsageLevelVariation {
  part def SspModel;

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
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;

    variation part source : SignalSource {
      variant part stepSource : Step;
      variant part sineSource : Sine;
    }

    part gain : Gain;
    connect source.y to gain.u;
  }
}
