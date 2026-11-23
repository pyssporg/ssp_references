package VariationBodyGain {
  private import PysspCore::*;

  attribute def VariationBodyGainDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  /* One variation point: its variants are bodies, not types. */
  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part oneStage {
      part gain : Gain;
      connect u to gain.u;
      connect gain.y to y;
    }

    variant part twoStages {
      part product : Product;
      part gain : Gain;
      connect u to product.u1;
      connect u to product.u2;
      connect product.y to gain.u;
      connect gain.y to y;
    }
  }

  part def System :> SspModel {
    attribute defaults : VariationBodyGainDefaultExperiment;

    part source : Sine;
    part path : PathChoice;
    connect source.y to path.u;

  }

  /* Configurations: each binds the path point to one variant body. */
  part def OneStageSystem :> System {
    part :>> path = PathChoice::oneStage;
  }

  part def TwoStagesSystem :> System {
    part :>> path = PathChoice::twoStages;
  }
}
