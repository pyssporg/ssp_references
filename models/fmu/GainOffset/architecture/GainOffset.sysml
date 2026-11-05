package GainOffset {

  port def GeneratorParameters :> ParameterInterface {
    attribute gain : Real = 2.0;
    attribute offset : Real = 0.5;
    attribute frequency : Real = 1.0;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def GeneratorFmu :> FmuMetadata {
    attribute source = "artifacts/build/GainOffset/Generator.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Generator {
    doc /* Analytic source: y = offset + gain * sin(2 * pi * frequency * t). */
    attribute fmu_meta : GeneratorFmu;
    in port parameters : GeneratorParameters;
    out port y : RealSignal;
  }

  /* The generator exports components below a composition root; this root holds
   * the FMU's single component. */
  part def Fmu {
    part generator : Generator;
  }
}
