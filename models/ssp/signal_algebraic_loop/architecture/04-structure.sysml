package SignalAlgebraicLoop {
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part sine : Sine;
    part gain : Gain;
    part add : Add;
    connect sine.y to add.u1;
    connect gain.y to add.u2;
    connect add.y to gain.u;
  }
}
