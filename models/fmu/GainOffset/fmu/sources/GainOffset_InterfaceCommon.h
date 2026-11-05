#ifndef GAINOFFSET_INTERFACECOMMON_H
#define GAINOFFSET_INTERFACECOMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Generated from architecture package GainOffset. Do not edit manually. */

typedef struct GainOffset_RealSignal {
  double value;
} GainOffset_RealSignal;

typedef enum GainOffset_DataType {
  GAINOFFSET_DATA_NONE = 0,
  GAINOFFSET_DATA_REAL = 1,
  GAINOFFSET_DATA_INTEGER = 2,
  GAINOFFSET_DATA_BOOLEAN = 3,
  GAINOFFSET_DATA_STRING = 4,
} GainOffset_DataType;

typedef struct GainOffset_VrMapping {
  void* data;
  GainOffset_DataType type;
  bool writable;
} GainOffset_VrMapping;

#endif  /* GAINOFFSET_INTERFACECOMMON_H */
