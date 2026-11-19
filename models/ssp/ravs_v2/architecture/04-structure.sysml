package RavsV2 {
  private import PysspCore::*;

  attribute def RavsV2DefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
  }

  part def System :> SspModel {
    attribute defaults : RavsV2DefaultExperiment;

    part adaption : adaption;
    part atmos : atmos;
    part consumer : consumer;
    part ecs_hw : ecs_hw;
    part ecs_sw : ecs_sw;
    part fuel : fuel;
    part valve : valve;

    connect valve.p1 to fuel.valve_p1;
    connect valve.p2 to fuel.valve_p2;
    connect valve.p3 to fuel.valve_p3;
    connect valve.u to fuel.valve_u;
    connect fuel.valve_mflowA to valve.mflowA;
    connect fuel.valve_mflowB to valve.mflowB;
    connect atmos.Tamb to ecs_hw.Tamb;
    connect atmos.Pamb to ecs_hw.Pamb;
    connect atmos.Tamb to consumer.Tamb;
    connect atmos.Pamb to consumer.Pamb;
    connect atmos.Tamb to fuel.T_AMB;
    connect atmos.Pamb to fuel.P_AMB;
    connect ecs_hw.LHexTout to adaption.LHexTout;
    connect adaption.sWsignals to ecs_sw.Input;
    connect ecs_sw.TCoolingPack to ecs_hw.reqCoolingTemperature;
    connect ecs_hw.consumerFeed to consumer.consumerFeed;
    connect consumer.consumerRet to fuel.pmhn;
    connect fuel.pmh to ecs_hw.consumerRet;
  }
}
