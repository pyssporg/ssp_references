/* Example 01 -- model-level structural configuration.
 *
 * Standard anchor: SysML v2.0 Language §7.6.7 (variation, variant) and
 * §8.4.2.3; the 100% configuration pattern shown in the official
 * `VehicleVariabilityModel.sysml` example (`part :>> engine = ...`).
 *
 * The 150% model is `System`. Each configuration specializes it and binds the
 * variation usage to one declared variant with a redefinition and a feature
 * value. The analysis composes the configuration, not `System`.
 *
 * Derived selection maps:
 *   StepSystem  -> {"source": "step"}
 *   SineSystem  -> {"source": "sine"}
 *
 * Probe on the pinned toolchain: the file loads, but the adapter records the
 * anonymous `:>> source` usage with type None; the redefinition target and the
 * feature value are lost. See IMP-106.
 */
package StructuralConfiguration {
  part def SspModel;
  part def Analysis;

  variation part def SourceChoice {
    variant part step : Step;
    variant part sine : Sine;
  }

  part def Step;
  part def Sine;

  part def System :> SspModel {
    part source : SourceChoice;
  }

  part def StepSystem :> System {
    part :>> source = SourceChoice::step;
  }

  part def SineSystem :> System {
    part :>> source = SourceChoice::sine;
  }

  part def step :> Analysis {
    part sut : StepSystem;
  }

  part def sine :> Analysis {
    part sut : SineSystem;
  }
}
