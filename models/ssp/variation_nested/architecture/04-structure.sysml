package VariationNested {
  variation part def StageChoice {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;

    variant part gainStage : GainStage;
    variant part secondStage : SecondStage;
  }

  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part directPath : DirectPath;
    variant part nestedPath : NestedPath;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Sine;
    part path : PathChoice;

    connect source.y to path.u;

  }

  /* Configurations: the outer binding selects the path variant; the nested
     binding exists only inside the specialized nested usage. */
  part def DirectSystem :> System {
    part :>> path = PathChoice::directPath;
  }

  part def NestedGainSystem :> System {
    part nestedGainPath :> PathChoice::nestedPath {
      part :>> inner_stage = StageChoice::gainStage;
    }
    part :>> path = nestedGainPath;
  }
}
