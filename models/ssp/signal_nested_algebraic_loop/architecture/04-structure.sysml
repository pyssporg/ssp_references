package SignalNestedAlgebraicLoop {
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part sine : Sine;
    part gain_outer : Gain;
    part gain_inner : Gain;
    part add_outer : Add;
    part add_inner : Add;
    connect sine.y to add_outer.u1;
    connect add_inner.y to add_outer.u2;
    connect add_outer.y to gain_outer.u;
    connect gain_outer.y to add_inner.u1;
    connect gain_inner.y to add_inner.u2;
    connect add_inner.y to gain_inner.u;
  }
}
