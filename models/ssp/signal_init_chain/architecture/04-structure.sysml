package SignalInitChain {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Sine;
    part gain : Gain;
    part add : Add;
    connect source.y to gain.u;
    connect gain.y to add.u1;
  }
}