package SignalInitLoopGuard {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part gain : LoopGain;
    part div : DivideGuard;
    connect gain.y to div.u;
    connect div.y to gain.u;
  }
}
