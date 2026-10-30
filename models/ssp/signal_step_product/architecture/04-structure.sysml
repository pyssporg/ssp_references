package SignalStepProduct {
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part sine : Sine;
    part product : Product;
    connect step.y to product.u1;
    connect sine.y to product.u2;
  }
}
