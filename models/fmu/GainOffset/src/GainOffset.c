/* FMI 2.0 CoSimulation source for the GainOffset fixture.
 *
 * The interface is authored in models/fmu/GainOffset/architecture/GainOffset.sysml
 * and emitted by pyfmi_sysml2 into GainOffset_InterfaceCommon.h and
 * GainOffset_Generator.h.
 * This file never spells a numeric value reference: every entry of the mapping
 * table is indexed by the generated enumerator, so a change in the authored
 * variable set or order moves the binary with the headers and the
 * modelDescription instead of drifting away from them.
 *
 * The model is a pure algebraic source, so the closed form below is the
 * expected trajectory: y(t) = offset + gain * sin(2 * pi * frequency * t).
 */

#include <math.h>
#include <stdlib.h>

#include "GainOffset_Generator.h"
#include "fmi2Functions.h"

#define PI 3.14159265358979323846
#define MODEL_NAME "Fmu.Generator"

/* Start values, identical to the defaults authored in GeneratorParameters. */
#define GAIN_DEFAULT 2.0
#define OFFSET_DEFAULT 0.5
#define FREQUENCY_DEFAULT 1.0

typedef struct {
    fmi2CallbackFunctions callbacks;
    fmi2ComponentEnvironment environment;
    fmi2Real time;
    fmi2Real gain;
    fmi2Real offset;
    fmi2Real frequency;
    GainOffset_RealSignal y;
    GainOffset_VrMapping vr_map[GainOffset_Generator_VrCount];
} Generator;

static void log_message(Generator* model, fmi2Status status, const char* message) {
    if (model->callbacks.logger != NULL) {
        model->callbacks.logger(
            model->environment, MODEL_NAME, status, "GainOffset", message);
    }
}

static void evaluate(Generator* model) {
    model->y.value =
        model->offset + model->gain * sin(2.0 * PI * model->frequency * model->time);
}

/* Mirror of the generated C++ helper GainOffset_Generator_initialize_vr_map,
 * written against the C-only part of the same header. */
static void map_value_references(Generator* model) {
    size_t vr;

    for (vr = 0; vr < GainOffset_Generator_VrCount; ++vr) {
        model->vr_map[vr].data = NULL;
        model->vr_map[vr].type = GAINOFFSET_DATA_NONE;
        model->vr_map[vr].writable = false;
    }

    model->vr_map[GAINOFFSET_GENERATOR_VR_GAIN].data = &model->gain;
    model->vr_map[GAINOFFSET_GENERATOR_VR_GAIN].type = GAINOFFSET_DATA_REAL;
    model->vr_map[GAINOFFSET_GENERATOR_VR_GAIN].writable = true;

    model->vr_map[GAINOFFSET_GENERATOR_VR_OFFSET].data = &model->offset;
    model->vr_map[GAINOFFSET_GENERATOR_VR_OFFSET].type = GAINOFFSET_DATA_REAL;
    model->vr_map[GAINOFFSET_GENERATOR_VR_OFFSET].writable = true;

    model->vr_map[GAINOFFSET_GENERATOR_VR_FREQUENCY].data = &model->frequency;
    model->vr_map[GAINOFFSET_GENERATOR_VR_FREQUENCY].type = GAINOFFSET_DATA_REAL;
    model->vr_map[GAINOFFSET_GENERATOR_VR_FREQUENCY].writable = true;

    model->vr_map[GAINOFFSET_GENERATOR_VR_Y_VALUE].data = &model->y.value;
    model->vr_map[GAINOFFSET_GENERATOR_VR_Y_VALUE].type = GAINOFFSET_DATA_REAL;
    model->vr_map[GAINOFFSET_GENERATOR_VR_Y_VALUE].writable = false;
}

static void reset_state(Generator* model) {
    model->time = 0.0;
    model->gain = GAIN_DEFAULT;
    model->offset = OFFSET_DEFAULT;
    model->frequency = FREQUENCY_DEFAULT;
    evaluate(model);
}

/* Every accessor below goes through vr_map, so the mapping table, not this
 * file's member names, decides which value reference reaches which slot. */
static GainOffset_VrMapping* entry_for(Generator* model, fmi2ValueReference vr) {
    if (vr >= GainOffset_Generator_VrCount) {
        return NULL;
    }
    return &model->vr_map[vr];
}

FMI2_Export const char* fmi2GetTypesPlatform(void) {
    return fmi2TypesPlatform;
}

FMI2_Export const char* fmi2GetVersion(void) {
    return fmi2Version;
}

FMI2_Export fmi2Status fmi2SetDebugLogging(
    fmi2Component c, fmi2Boolean loggingOn, size_t nCategories,
    const fmi2String categories[]) {
    (void)c;
    (void)loggingOn;
    (void)nCategories;
    (void)categories;
    return fmi2OK;
}

FMI2_Export fmi2Component fmi2Instantiate(
    fmi2String instanceName, fmi2Type fmuType, fmi2String fmuGUID,
    fmi2String fmuResourceLocation, const fmi2CallbackFunctions* functions,
    fmi2Boolean visible, fmi2Boolean loggingOn) {
    Generator* model;

    (void)instanceName;
    (void)fmuResourceLocation;
    (void)visible;
    (void)loggingOn;

    if (fmuType != fmi2CoSimulation || functions == NULL || functions->logger == NULL) {
        return NULL;
    }

    model = (Generator*)calloc(1, sizeof(Generator));
    if (model == NULL) {
        return NULL;
    }
    model->callbacks = *functions;
    model->environment = functions->componentEnvironment;
    map_value_references(model);
    reset_state(model);
    return (fmi2Component)model;
}

FMI2_Export void fmi2FreeInstance(fmi2Component c) {
    free(c);
}

FMI2_Export fmi2Status fmi2SetupExperiment(
    fmi2Component c, fmi2Boolean toleranceDefined, fmi2Real tolerance,
    fmi2Real startTime, fmi2Boolean stopTimeDefined, fmi2Real stopTime) {
    Generator* model = (Generator*)c;

    (void)toleranceDefined;
    (void)tolerance;
    (void)stopTimeDefined;
    (void)stopTime;
    if (model == NULL) {
        return fmi2Error;
    }
    model->time = startTime;
    evaluate(model);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2EnterInitializationMode(fmi2Component c) {
    Generator* model = (Generator*)c;

    if (model == NULL) {
        return fmi2Error;
    }
    evaluate(model);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2ExitInitializationMode(fmi2Component c) {
    Generator* model = (Generator*)c;

    if (model == NULL) {
        return fmi2Error;
    }
    log_message(model, fmi2OK, "initialization complete");
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2Terminate(fmi2Component c) {
    return c == NULL ? fmi2Error : fmi2OK;
}

FMI2_Export fmi2Status fmi2Reset(fmi2Component c) {
    Generator* model = (Generator*)c;

    if (model == NULL) {
        return fmi2Error;
    }
    reset_state(model);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2GetReal(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    fmi2Real value[]) {
    Generator* model = (Generator*)c;
    size_t index;

    if (model == NULL || vr == NULL || value == NULL) {
        return fmi2Error;
    }
    for (index = 0; index < nvr; ++index) {
        GainOffset_VrMapping* entry = entry_for(model, vr[index]);
        if (entry == NULL || entry->data == NULL || entry->type != GAINOFFSET_DATA_REAL) {
            return fmi2Error;
        }
        value[index] = *(fmi2Real*)entry->data;
    }
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2SetReal(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    const fmi2Real value[]) {
    Generator* model = (Generator*)c;
    size_t index;

    if (model == NULL || vr == NULL || value == NULL) {
        return fmi2Error;
    }
    for (index = 0; index < nvr; ++index) {
        GainOffset_VrMapping* entry = entry_for(model, vr[index]);
        if (entry == NULL || entry->data == NULL || entry->type != GAINOFFSET_DATA_REAL) {
            return fmi2Error;
        }
        if (!entry->writable) {
            log_message(model, fmi2Error, "value reference is not writable");
            return fmi2Error;
        }
        *(fmi2Real*)entry->data = value[index];
    }
    evaluate(model);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2GetInteger(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    fmi2Integer value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SetInteger(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    const fmi2Integer value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetBoolean(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    fmi2Boolean value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SetBoolean(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    const fmi2Boolean value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetString(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    fmi2String value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SetString(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
    const fmi2String value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SetRealInputDerivatives(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer order[],
    const fmi2Real value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)order;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetRealOutputDerivatives(
    fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer order[],
    fmi2Real value[]) {
    (void)c;
    (void)vr;
    (void)nvr;
    (void)order;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2DoStep(
    fmi2Component c, fmi2Real currentCommunicationPoint,
    fmi2Real communicationStepSize, fmi2Boolean noSetFMUStatePriorToCurrentPoint) {
    Generator* model = (Generator*)c;

    (void)noSetFMUStatePriorToCurrentPoint;
    if (model == NULL || communicationStepSize < 0.0) {
        return fmi2Error;
    }
    model->time = currentCommunicationPoint + communicationStepSize;
    evaluate(model);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2CancelStep(fmi2Component c) {
    return c == NULL ? fmi2Error : fmi2OK;
}

FMI2_Export fmi2Status fmi2GetStatus(
    fmi2Component c, const fmi2StatusKind s, fmi2Status* value) {
    (void)c;
    (void)s;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetRealStatus(
    fmi2Component c, const fmi2StatusKind s, fmi2Real* value) {
    Generator* model = (Generator*)c;

    if (model == NULL || value == NULL) {
        return fmi2Error;
    }
    if (s == fmi2LastSuccessfulTime) {
        *value = model->time;
        return fmi2OK;
    }
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetIntegerStatus(
    fmi2Component c, const fmi2StatusKind s, fmi2Integer* value) {
    (void)c;
    (void)s;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetBooleanStatus(
    fmi2Component c, const fmi2StatusKind s, fmi2Boolean* value) {
    Generator* model = (Generator*)c;

    if (model == NULL || value == NULL) {
        return fmi2Error;
    }
    if (s == fmi2Terminated) {
        *value = fmi2False;
        return fmi2OK;
    }
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetStringStatus(
    fmi2Component c, const fmi2StatusKind s, fmi2String* value) {
    (void)c;
    (void)s;
    (void)value;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetFMUstate(fmi2Component c, fmi2FMUstate* FMUstate) {
    (void)c;
    (void)FMUstate;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SetFMUstate(fmi2Component c, fmi2FMUstate FMUstate) {
    (void)c;
    (void)FMUstate;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2FreeFMUstate(fmi2Component c, fmi2FMUstate* FMUstate) {
    (void)c;
    (void)FMUstate;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SerializedFMUstateSize(
    fmi2Component c, fmi2FMUstate FMUstate, size_t* size) {
    (void)c;
    (void)FMUstate;
    (void)size;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2SerializeFMUstate(
    fmi2Component c, fmi2FMUstate FMUstate, fmi2Byte serializedState[], size_t size) {
    (void)c;
    (void)FMUstate;
    (void)serializedState;
    (void)size;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2DeSerializeFMUstate(
    fmi2Component c, const fmi2Byte serializedState[], size_t size,
    fmi2FMUstate* FMUstate) {
    (void)c;
    (void)serializedState;
    (void)size;
    (void)FMUstate;
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetDirectionalDerivative(
    fmi2Component c, const fmi2ValueReference vUnknown_ref[], size_t nUnknown,
    const fmi2ValueReference vKnown_ref[], size_t nKnown, const fmi2Real dvKnown[],
    fmi2Real dvUnknown[]) {
    (void)c;
    (void)vUnknown_ref;
    (void)nUnknown;
    (void)vKnown_ref;
    (void)nKnown;
    (void)dvKnown;
    (void)dvUnknown;
    return fmi2Error;
}
