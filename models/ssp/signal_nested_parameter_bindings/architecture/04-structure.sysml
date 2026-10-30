package SignalNestedParameterBindings {
  part def System :> SspModel {
    out port y : RealSignal;
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part add : Add;
    part inner : Inner;
    connect step.y to add.u1;
    connect inner.y to add.u2;
    connect add.y to y;
  }
}
