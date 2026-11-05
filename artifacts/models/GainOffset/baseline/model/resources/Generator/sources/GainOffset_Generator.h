#ifndef GAINOFFSET_GENERATOR_H
#define GAINOFFSET_GENERATOR_H

#include "GainOffset_InterfaceCommon.h"

/* Generated interface for GainOffset.Generator. Do not edit manually. */

typedef enum GainOffset_Generator_ValueReference {
  GAINOFFSET_GENERATOR_VR_GAIN = 0,
  GAINOFFSET_GENERATOR_VR_OFFSET = 1,
  GAINOFFSET_GENERATOR_VR_FREQUENCY = 2,
  GAINOFFSET_GENERATOR_VR_Y_VALUE = 3,
} GainOffset_Generator_ValueReference;

enum { GainOffset_Generator_VrCount = 4 };

#ifdef __cplusplus
#include <string>

struct GainOffset_Generator_Instance {
  GainOffset_VrMapping vr_map[4] = {};
  double gain = 2;
  double offset = 0.5;
  double frequency = 1;
  GainOffset_RealSignal y = {};
};

inline void GainOffset_Generator_initialize_vr_map(GainOffset_Generator_Instance* instance) {
  for (size_t i = 0; i < GainOffset_Generator_VrCount; ++i) {
    instance->vr_map[i] = {nullptr, GAINOFFSET_DATA_NONE, false};
  }
  instance->vr_map[GAINOFFSET_GENERATOR_VR_GAIN] = {&instance->gain, GAINOFFSET_DATA_REAL, true};
  instance->vr_map[GAINOFFSET_GENERATOR_VR_OFFSET] = {&instance->offset, GAINOFFSET_DATA_REAL, true};
  instance->vr_map[GAINOFFSET_GENERATOR_VR_FREQUENCY] = {&instance->frequency, GAINOFFSET_DATA_REAL, true};
  instance->vr_map[GAINOFFSET_GENERATOR_VR_Y_VALUE] = {&instance->y.value, GAINOFFSET_DATA_REAL, false};
}

#endif  /* __cplusplus */
#endif  /* GAINOFFSET_GENERATOR_H */