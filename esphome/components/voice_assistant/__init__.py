import esphome.config_validation as cv
import esphome.codegen as cg

from esphome.const import (
    CONF_ID,
    CONF_MICROPHONE,
    CONF_SPEAKER,
    CONF_MEDIA_PLAYER,
    CONF_ON_CLIENT_CONNECTED,
    CONF_ON_CLIENT_DISCONNECTED,
)
from esphome.core import CORE
from esphome import automation
from esphome.automation import register_action, register_condition
from esphome.components import microphone, speaker, media_player, esp32

AUTO_LOAD = ["socket"]
DEPENDENCIES = ["api", "microphone"]

CODEOWNERS = ["@jesserockz"]

CONF_ON_END = "on_end"
CONF_ON_ERROR = "on_error"
CONF_ON_INTENT_END = "on_intent_end"
CONF_ON_INTENT_START = "on_intent_start"
CONF_ON_LISTENING = "on_listening"
CONF_ON_START = "on_start"
CONF_ON_STT_END = "on_stt_end"
CONF_ON_STT_VAD_END = "on_stt_vad_end"
CONF_ON_STT_VAD_START = "on_stt_vad_start"
CONF_ON_TTS_END = "on_tts_end"
CONF_ON_TTS_START = "on_tts_start"
CONF_ON_TTS_STREAM_START = "on_tts_stream_start"
CONF_ON_TTS_STREAM_END = "on_tts_stream_end"
CONF_ON_WAKE_WORD_DETECTED = "on_wake_word_detected"

CONF_SILENCE_DETECTION = "silence_detection"
CONF_USE_WAKE_WORD = "use_wake_word"
CONF_USE_LOCAL_WAKE_WORD = "use_local_wake_word"
CONF_VAD_THRESHOLD = "vad_threshold"

CONF_AUTO_GAIN = "auto_gain"
CONF_NOISE_SUPPRESSION_LEVEL = "noise_suppression_level"
CONF_VOLUME_MULTIPLIER = "volume_multiplier"


voice_assistant_ns = cg.esphome_ns.namespace("voice_assistant")
VoiceAssistant = voice_assistant_ns.class_("VoiceAssistant", cg.Component)

StartAction = voice_assistant_ns.class_(
    "StartAction", automation.Action, cg.Parented.template(VoiceAssistant)
)
StartContinuousAction = voice_assistant_ns.class_(
    "StartContinuousAction", automation.Action, cg.Parented.template(VoiceAssistant)
)
StopAction = voice_assistant_ns.class_(
    "StopAction", automation.Action, cg.Parented.template(VoiceAssistant)
)
IsRunningCondition = voice_assistant_ns.class_(
    "IsRunningCondition", automation.Condition, cg.Parented.template(VoiceAssistant)
)
ConnectedCondition = voice_assistant_ns.class_(
    "ConnectedCondition", automation.Condition, cg.Parented.template(VoiceAssistant)
)


def tts_stream_validate(config):
    if CONF_SPEAKER not in config and (
        CONF_ON_TTS_STREAM_START in config or CONF_ON_TTS_STREAM_END in config
    ):
        raise cv.Invalid(
            f"{CONF_SPEAKER} is required when using {CONF_ON_TTS_STREAM_START} and/or {CONF_ON_TTS_STREAM_END}"
        )
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(VoiceAssistant),
            cv.GenerateID(CONF_MICROPHONE): cv.use_id(microphone.Microphone),
            cv.Exclusive(CONF_SPEAKER, "output"): cv.use_id(speaker.Speaker),
            cv.Exclusive(CONF_MEDIA_PLAYER, "output"): cv.use_id(
                media_player.MediaPlayer
            ),
            cv.Optional(CONF_USE_WAKE_WORD, default=False): cv.boolean,
            cv.Optional(CONF_USE_LOCAL_WAKE_WORD, default=False): cv.boolean,
            cv.Optional(CONF_VAD_THRESHOLD): cv.All(cv.uint8_t),
            cv.Optional(CONF_NOISE_SUPPRESSION_LEVEL, default=0): cv.int_range(0, 4),
            cv.Optional(CONF_AUTO_GAIN, default="0dBFS"): cv.All(
                cv.float_with_unit("decibel full scale", "(dBFS|dbfs|DBFS)"),
                cv.int_range(0, 31),
            ),
            cv.Optional(CONF_VOLUME_MULTIPLIER, default=1.0): cv.float_range(
                min=0.0, min_included=False
            ),
            cv.Optional(CONF_ON_LISTENING): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_START): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_WAKE_WORD_DETECTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_STT_END): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_TTS_START): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_TTS_END): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_END): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_ERROR): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_CLIENT_CONNECTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_CLIENT_DISCONNECTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_INTENT_START): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_INTENT_END): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_STT_VAD_START): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_STT_VAD_END): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TTS_STREAM_START): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TTS_STREAM_END): automation.validate_automation(
                single=True
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    tts_stream_validate,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))

    if CONF_SPEAKER in config:
        spkr = await cg.get_variable(config[CONF_SPEAKER])
        cg.add(var.set_speaker(spkr))

    if CONF_MEDIA_PLAYER in config:
        mp = await cg.get_variable(config[CONF_MEDIA_PLAYER])
        cg.add(var.set_media_player(mp))

    cg.add(var.set_use_wake_word(config[CONF_USE_WAKE_WORD]))
    cg.add(var.set_use_local_wake_word(config[CONF_USE_LOCAL_WAKE_WORD]))

    if (vad_threshold := config.get(CONF_VAD_THRESHOLD)) is not None:
        cg.add(var.set_vad_threshold(vad_threshold))

    cg.add(var.set_noise_suppression_level(config[CONF_NOISE_SUPPRESSION_LEVEL]))
    cg.add(var.set_auto_gain(config[CONF_AUTO_GAIN]))
    cg.add(var.set_volume_multiplier(config[CONF_VOLUME_MULTIPLIER]))

    if CONF_ON_LISTENING in config:
        await automation.build_automation(
            var.get_listening_trigger(), [], config[CONF_ON_LISTENING]
        )

    if CONF_ON_START in config:
        await automation.build_automation(
            var.get_start_trigger(), [], config[CONF_ON_START]
        )

    if CONF_ON_WAKE_WORD_DETECTED in config:
        await automation.build_automation(
            var.get_wake_word_detected_trigger(),
            [],
            config[CONF_ON_WAKE_WORD_DETECTED],
        )

    if CONF_ON_STT_END in config:
        await automation.build_automation(
            var.get_stt_end_trigger(), [(cg.std_string, "x")], config[CONF_ON_STT_END]
        )

    if CONF_ON_TTS_START in config:
        await automation.build_automation(
            var.get_tts_start_trigger(),
            [(cg.std_string, "x")],
            config[CONF_ON_TTS_START],
        )

    if CONF_ON_TTS_END in config:
        await automation.build_automation(
            var.get_tts_end_trigger(), [(cg.std_string, "x")], config[CONF_ON_TTS_END]
        )

    if CONF_ON_END in config:
        await automation.build_automation(
            var.get_end_trigger(), [], config[CONF_ON_END]
        )

    if CONF_ON_ERROR in config:
        await automation.build_automation(
            var.get_error_trigger(),
            [(cg.std_string, "code"), (cg.std_string, "message")],
            config[CONF_ON_ERROR],
        )

    if CONF_ON_CLIENT_CONNECTED in config:
        await automation.build_automation(
            var.get_client_connected_trigger(),
            [],
            config[CONF_ON_CLIENT_CONNECTED],
        )

    if CONF_ON_CLIENT_DISCONNECTED in config:
        await automation.build_automation(
            var.get_client_disconnected_trigger(),
            [],
            config[CONF_ON_CLIENT_DISCONNECTED],
        )

    if CONF_ON_INTENT_START in config:
        await automation.build_automation(
            var.get_intent_start_trigger(),
            [],
            config[CONF_ON_INTENT_START],
        )

    if CONF_ON_INTENT_END in config:
        await automation.build_automation(
            var.get_intent_end_trigger(),
            [],
            config[CONF_ON_INTENT_END],
        )

    if CONF_ON_STT_VAD_START in config:
        await automation.build_automation(
            var.get_stt_vad_start_trigger(),
            [],
            config[CONF_ON_STT_VAD_START],
        )

    if CONF_ON_STT_VAD_END in config:
        await automation.build_automation(
            var.get_stt_vad_end_trigger(),
            [],
            config[CONF_ON_STT_VAD_END],
        )

    if CONF_ON_TTS_STREAM_START in config:
        await automation.build_automation(
            var.get_tts_stream_start_trigger(),
            [],
            config[CONF_ON_TTS_STREAM_START],
        )

    if CONF_ON_TTS_STREAM_END in config:
        await automation.build_automation(
            var.get_tts_stream_end_trigger(),
            [],
            config[CONF_ON_TTS_STREAM_END],
        )

    cg.add_define("USE_VOICE_ASSISTANT")
    if CORE.using_esp_idf:
        esp32.add_idf_component(
            name="esp-tflite-micro",
            repo="https://github.com/espressif/esp-tflite-micro",
            # path="components",
            # components=["esp-radar"],
        )
        # esp32.add_idf_component(
        #     name="esp-nn",
        #     repo="https://github.com/espressif/esp-nn",
        #     # path="components",
        #     # components=["esp-radar"],
        # )
    if CORE.using_arduino:
#        cg.add_library(
#                name = "TFLite-Micro",
#                repository="https://github.com/h3ndrik/tflite-micro-arduino-library.git",
#                version="a30071d33b12cd29978febfbd7f1f90b1228a6c2"
#            )
        #cg.add_library("nickjgniklu/ESP_TF", "1.0.0")
        cg.add_library(
                name = "ESP_TF",
                repository="https://github.com/h3ndrik/ESP_TF.git",
                version="a41894f4b5a2c2d3e2268d875437592294594390"
            )

    cg.add_build_flag("-DTF_LITE_STATIC_MEMORY")
    cg.add_build_flag("-DTF_LITE_DISABLE_X86_NEON")
    cg.add_build_flag("-DESP_NN")
    cg.add_build_flag("-DCONFIG_IDF_TARGET_ESP32")
    # CONFIG_IDF_TARGET_ESP32S3


VOICE_ASSISTANT_ACTION_SCHEMA = cv.Schema({cv.GenerateID(): cv.use_id(VoiceAssistant)})


@register_action(
    "voice_assistant.start_continuous",
    StartContinuousAction,
    VOICE_ASSISTANT_ACTION_SCHEMA,
)
@register_action(
    "voice_assistant.start",
    StartAction,
    VOICE_ASSISTANT_ACTION_SCHEMA.extend(
        {
            cv.Optional(CONF_SILENCE_DETECTION, default=True): cv.boolean,
        }
    ),
)
async def voice_assistant_listen_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    if CONF_SILENCE_DETECTION in config:
        cg.add(var.set_silence_detection(config[CONF_SILENCE_DETECTION]))
    return var


@register_action("voice_assistant.stop", StopAction, VOICE_ASSISTANT_ACTION_SCHEMA)
async def voice_assistant_stop_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


@register_condition(
    "voice_assistant.is_running", IsRunningCondition, VOICE_ASSISTANT_ACTION_SCHEMA
)
async def voice_assistant_is_running_to_code(config, condition_id, template_arg, args):
    var = cg.new_Pvariable(condition_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


@register_condition(
    "voice_assistant.connected", ConnectedCondition, VOICE_ASSISTANT_ACTION_SCHEMA
)
async def voice_assistant_connected_to_code(config, condition_id, template_arg, args):
    var = cg.new_Pvariable(condition_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var
