package RavsV2 {
  private import ScalarValues::*;
  private import PysspCore::*;

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 10.0;

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
    connect ecs_hw.'consumerFeed.hn' to consumer.'consumerFeed.hn';
    connect ecs_hw.'consumerFeed.m' to consumer.'consumerFeed.m';
    connect consumer.consumerRet to fuel.pmhn;
    connect consumer.'consumerRet.hn' to fuel.'pmhn.hn';
    connect consumer.'consumerRet.m' to fuel.'pmhn.m';
    connect fuel.pmh to ecs_hw.consumerRet;
    connect fuel.'pmh.hn' to ecs_hw.'consumerRet.hn';
    connect fuel.'pmh.m' to ecs_hw.'consumerRet.m';
  }
}
