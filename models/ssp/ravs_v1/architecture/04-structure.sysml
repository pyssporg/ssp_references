package RavsV1 {
  private import PysspCore::*;

  attribute def RavsV1DefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
  }

  part def System :> SspModel {
    attribute defaults : RavsV1DefaultExperiment;

    part ECS_HW : ECS_HW;
    part ECS_SW : ECS_SW;
    part Consumer : Consumer;
    part Atmos : Atmos;
    part AdaptionUnit : AdaptionUnit;
    part BC : BC;

    connect Consumer.consumerFeed to ECS_HW.consumerFeed;
    connect Consumer.consumerRet to ECS_HW.consumerRet;
    connect ECS_HW.LHexTout to AdaptionUnit.LHexTout;
    connect AdaptionUnit.sWsignals to ECS_SW.Input;
    connect ECS_SW.TCoolingPack to ECS_HW.reqCoolingTemperature;
    connect Atmos.Tamb to Consumer.Tamb;
    connect Atmos.Pamb to Consumer.Pamb;
    connect Atmos.Tamb to ECS_HW.Tamb;
    connect Atmos.Pamb to ECS_HW.Pamb;
    connect BC.Alt to Consumer.Alt;
    connect BC.Alt to ECS_HW.Alt;
    connect BC.Alt to Atmos.Alt;
    connect BC.Mach to Consumer.Mach;
    connect BC.Mach to ECS_HW.Mach;
    connect BC.Mach to Atmos.Ma;
    connect BC.heatLoad to Consumer.heatLoad;
    connect BC.Aircraft_state to AdaptionUnit.Aircraft_State;
  }
}
