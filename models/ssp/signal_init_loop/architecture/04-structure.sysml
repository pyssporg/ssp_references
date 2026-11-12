package SignalInitLoop {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part gain_a : LoopGain;
    part gain_b : LoopGain;
    connect gain_a.y to gain_b.u;
    connect gain_b.y to gain_a.u;
  }
}
