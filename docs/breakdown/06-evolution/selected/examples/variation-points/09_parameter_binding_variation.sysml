/* Example 09 -- parameter binding variation: same topology, different values.
 *
 * Pattern: the composition is written once, with two components and one signal
 * connection, and no variation point inside it. The variation sits on the
 * analysis, where a parameter set is applied: the baseline, the late step and the
 * high gain alternatives carry the same attribute names with different values.
 * Every selection therefore produces the same part and connector structure and
 * differs only in the values bound to the same parameter ports.
 *
 * "bind" is a relationship, not a value: what this variation point selects is
 * a parameter set, and a binding is how that set reaches a port. The grammar
 * does admit BindingConnectorAsUsage among the VariantUsageElement
 * alternatives, so "variant bind a.k = set.k;" is writable; but then the
 * selected alternative is a connector, not a set, and the values it applies
 * still have to come from a set usage somewhere. SSP represents the applied
 * set, not the connector: a build exports one SSV per set plus the SSM that
 * maps it. The variation is therefore declared over the usage that owns the
 * set, and the binding sits inside each variant, so that selecting a variant
 * selects both the values and the binds that apply them. The enclosing
 * composition never changes, which is the property this example is about.
 *
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership) for the point on the analysis. The body form is confirmed by
 * the grammar: VariantUsageMember is "variant" followed by VariantUsageElement,
 * whose PartUsage alternative reaches Usage -> UsageCompletion -> UsageBody ->
 * DefinitionBody; the usage declaration is optional, so "variant part name
 * { ... }" is legal, and DefinitionBody admits both AttributeUsage (the
 * parameter set usage) and BindingConnectorAsUsage (the bind). Grammar source:
 * Systems-Modeling/SysML-v2-Pilot-Implementation,
 * org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext, rules
 * VariantUsageMember, VariantUsageElement, PartUsage, Usage, UsageBody,
 * DefinitionBody and BindingConnectorAsUsage. Binding connectors fall under
 * the connection clauses of specification section 7.12.
 *
 * Expected SSP/FMI mapping: the parts and connections of SystemStructure.ssd
 * are the same in every selection: two <Part> entries (step, gain), one
 * <ssd:Connection> from step.y to gain.u, and the same connector
 * declarations, because neither a part nor a connector sits inside the
 * variation. Only the applied set changes: one SSV with the same four member
 * names and different values, and an SSM whose entries stay identical as long
 * as the member names do. Byte-identity of the SSD holds when the build writes
 * the selected set under one fixed resource name, as the fixtures in this
 * repository do; if the SSV is named after the set definition instead, the only
 * differing byte is the ssd:ParameterBinding source reference, never the
 * structure. A comparison of two selections is therefore a value comparison
 * over one structure, never a structural one.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors. The
 * parsed model keeps System exactly as written and keeps the analysis, but the
 * variation usage "parameters" survives with no variant members: the three
 * variant usages, their parameter set attributes and all their binds are
 * dropped. The variation usage itself survives as an ordinary part usage named
 * "parameters" typed by the empty ParameterBinding definition, since the usage,
 * not its members, is what the parser keeps. Generation of System therefore
 * succeeds and its SSD carries step and gain with their parameter connectors,
 * the single step.y to gain.u connection, and no parameter binding element at
 * all, because the binds lived inside the variants. The adapter cannot see a
 * binding that a selection would have chosen, so it also cannot emit the SSV
 * for it.
 */
package ParameterBindingVariation {
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

  attribute def BaselineValues :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 3.0;
  }

  attribute def LateStepValues :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.75;
    attribute k = 3.0;
  }

  attribute def HighGainValues :> ParameterSet {
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

  /* Fixed topology. No variation point appears anywhere inside it. */
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }

  /* Marker type for the binding point: the alternative adds no ports, only
   * values, so the variation usage has no interface of its own. */
  part def ParameterBinding;

  part def test_selected :> Analysis {
    doc /* One analysis per selection; the topology is the same composition. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;

    variation part parameters : ParameterBinding {
      variant part baselineBinding {
        attribute values : BaselineValues;
        bind sut.step.parameters.height = values.height;
        bind sut.step.parameters.offset = values.offset;
        bind sut.step.parameters.startTime = values.startTime;
        bind sut.gain.parameters.k = values.k;
      }

      variant part lateStepBinding {
        attribute values : LateStepValues;
        bind sut.step.parameters.height = values.height;
        bind sut.step.parameters.offset = values.offset;
        bind sut.step.parameters.startTime = values.startTime;
        bind sut.gain.parameters.k = values.k;
      }

      variant part highGainBinding {
        attribute values : HighGainValues;
        bind sut.step.parameters.height = values.height;
        bind sut.step.parameters.offset = values.offset;
        bind sut.step.parameters.startTime = values.startTime;
        bind sut.gain.parameters.k = values.k;
      }
    }
  }
}
