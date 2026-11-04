/* Example 02 -- model-level configuration with nested selection.
 *
 * Standard anchor: SysML v2.0 Language §7.6.7 and §8.4.2.3. This file is the
 * hard case: the inner variation point exists only inside the selected outer
 * variant body, so a configuration cannot bind the inner point on the original
 * outer usage.
 *
 * Shape that works structurally:
 *   - declare a usage that specializes the declared outer variant
 *     (`nestedGainPath :> PathChoice::nestedPath`);
 *   - inside that usage, redefine the inherited inner point
 *     (`part :>> inner_stage = StageChoice::gainStage`);
 *   - bind the outer point to that usage
 *     (`part :>> path = nestedGainPath`).
 *
 * Derived maps:
 *   DirectSystem     -> {"path": "directPath"}
 *   NestedGainSystem -> {"path": "nestedPath", "path.inner_stage": "gainStage"}
 *
 * Shapes that do not work:
 *   - `part :>> path = PathChoice::nestedPath;`
 *     plus `part :>> path.inner_stage = StageChoice::gainStage;`
 *     There is no feature `path.inner_stage` on the variation point; the inner
 *     point belongs to the variant's type, which the outer feature value does
 *     not redefine.
 *   - `part def NestedGainPath :> NestedPath { ... }` and
 *     `part :>> path : NestedGainPath;`
 *     `NestedGainPath` is not a subtype of `PathChoice`, so the redefined
 *     feature type is incompatible.
 *
 * Probe on the pinned toolchain: `nestedGainPath` loads with type None and its
 * body is dropped; the anonymous `:>> path` usage has no value. The adapter
 * needs redefinition and feature-value capture before it can derive the map.
 */
package NestedConfiguration {
  part def SspModel;
  part def Analysis;

  part def Gain;

  part def DirectPath {
    part gain : Gain;
  }

  variation part def StageChoice {
    variant part gainStage : Gain;
    variant part secondStage : Gain;
  }

  part def NestedPath {
    part output_gain : Gain;
    variation part inner_stage : StageChoice;
  }

  variation part def PathChoice {
    variant part directPath : DirectPath;
    variant part nestedPath : NestedPath;
  }

  part def System :> SspModel {
    part path : PathChoice;
  }

  part def DirectSystem :> System {
    part :>> path = PathChoice::directPath;
  }

  part def NestedGainSystem :> System {
    part nestedGainPath :> PathChoice::nestedPath {
      part :>> inner_stage = StageChoice::gainStage;
    }
    part :>> path = nestedGainPath;
  }

  part def direct :> Analysis {
    part sut : DirectSystem;
  }

  part def nested_gain :> Analysis {
    part sut : NestedGainSystem;
  }
}
