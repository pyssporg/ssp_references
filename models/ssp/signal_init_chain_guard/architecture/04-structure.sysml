package SignalInitChainGuard {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Sine;
    part guard : InitGuard;
    part add : Add;
    connect source.y to guard.u;
    connect guard.y to add.u1;
  }
}
