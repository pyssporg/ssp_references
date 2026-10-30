package SignalDelayDetector {
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain_a : Gain;
    part gain_b : Gain;
    part add : Add;
    connect step.y to gain_a.u;
    connect gain_a.y to gain_b.u;
    connect gain_b.y to add.u1;
    connect step.y to add.u2;
  }
}
