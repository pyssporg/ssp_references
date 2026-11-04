/* Example 01 -- structural part variation: choice-of-one over parts.
 *
 * Pattern: a composed system whose source stage is one of two interchangeable
 * implementations. The variation point is a definition ("variation part def")
 * whose variant members name the alternatives; the composition uses the
 * variation definition as the type of one part usage.
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership).
 *
 * Expected SSP/FMI mapping: exactly one variant is selected at build time and
 * becomes one <Part> in SystemStructure.ssd, typed by the FMU that the chosen
 * variant's fmu_meta names. The other variant contributes nothing: no part, no
 * connector, no FMU resource. Both alternatives already exist as independent
 * FMU fixtures with the same output port, so selection changes which FMU
 * resource is packaged and connected -- no FMI concept is added.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors, but the
 * parsed model has no variation flag and no variant members. SourceChoice is
 * an empty ordinary part definition with no parts and no ports, so generation
 * fails while resolving the connector, before selection could occur:
 * ValueError: Unknown port 'source.y' in connection.
 */
package StructuralPartVariation {
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

  variation part def SourceChoice {
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : Gain;
    connect source.y to gain.u;
  }
}
