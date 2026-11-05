package Embrace {
  private import ScalarValues::*;
  private import PysspCore::*;
  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 10.0;

    part ECS_HW : ECS_HW;
    part ECS_SW : ECS_SW;
    part Consumer : Consumer;
    part Atmos : Atmos;
    part AdaptionUnit : AdaptionUnit;
    part BC : BC;

    connect Consumer.'consumerFeed.X' to ECS_HW.'consumerFeed.X';
    connect Consumer.'consumerFeed.p' to ECS_HW.'consumerFeed.p';
    connect Consumer.'consumerFeed.h' to ECS_HW.'consumerFeed.h';
    connect Consumer.'consumerRet.p' to ECS_HW.'consumerRet.p';
    connect Consumer.'consumerRet.h' to ECS_HW.'consumerRet.h';
    connect Consumer.'consumerRet.X' to ECS_HW.'consumerRet.X';
    connect ECS_HW.'consumerFeed.m' to Consumer.'consumerFeed.m';
    connect ECS_HW.'consumerFeed.hn' to Consumer.'consumerFeed.hn';
    connect ECS_HW.'consumerRet.m' to Consumer.'consumerRet.m';
    connect ECS_HW.'consumerRet.hn' to Consumer.'consumerRet.hn';
    connect ECS_HW.LHexTout to AdaptionUnit.LHexTout;
    connect AdaptionUnit.'sWsignals.Aircraft_State' to ECS_SW.'Input.Aircraft_State';
    connect AdaptionUnit.'sWsignals.TLiquid' to ECS_SW.'Input.TLiquid';
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
