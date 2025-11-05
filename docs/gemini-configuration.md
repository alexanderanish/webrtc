# Gemini Live API Configuration Guide

This document provides a comprehensive guide to all configurable features of the Gemini Live API integration in the WebRTC Enterprise library.

## Table of Contents

1. [Push-to-Talk Feature](#push-to-talk-feature)
2. [Model Configuration](#model-configuration)
3. [Response Configuration](#response-configuration)
4. [Generation Settings](#generation-settings)
5. [Voice Configuration](#voice-configuration)
6. [Speech Configuration](#speech-configuration)
7. [Transcription Settings](#transcription-settings)
8. [Native Audio Features](#native-audio-features)
9. [Session Management](#session-management)
10. [Tools & Function Calling](#tools--function-calling)
11. [Frontend Usage](#frontend-usage)

## Push-to-Talk Feature

The WebRTC client includes a built-in push-to-talk (PTT) feature that gives users precise control over when audio is transmitted.

### Features

- **Toggle Mode**: Switch between PTT mode and always-on audio mode with a checkbox
- **Multiple Input Methods**:
  - Hold the PTT button with mouse or touch
  - Press and hold the Space bar (default) on keyboard
- **Visual Feedback**:
  - Large circular button changes color when active
  - Pulsing animation while transmitting
  - Status indicator shows "Transmitting" or "Standby"
- **Smart Detection**: Keyboard shortcut is disabled when typing in input fields
- **Efficient**: Mutes/unmutes audio tracks without stopping the stream

### Usage

1. **Start Audio**: Click "Start Audio" to begin streaming
2. **Enable PTT**: Check the "Push-to-Talk Mode" checkbox
3. **Transmit**:
   - Hold down the circular PTT button, OR
   - Press and hold the Space bar
4. **Release**: Audio stops transmitting when you release

### Benefits with Gemini Live

- **Reduces bandwidth**: Only transmits when you're actively speaking
- **Better VAD integration**: Works seamlessly with Voice Activity Detection
- **Privacy**: Prevents accidental audio transmission
- **Professional conversations**: Gives control similar to radio/walkie-talkie communication

### Technical Details

PTT mode works by enabling/disabling the audio tracks without stopping the entire media stream:

```typescript
// Enable audio transmission
audioTrack.enabled = true;

// Disable audio transmission (mute)
audioTrack.enabled = false;
```

This approach is more efficient than starting/stopping the stream repeatedly.

## Model Configuration

### Available Models

- `gemini-2.0-flash-exp` - Fast, general-purpose model
- `gemini-live-2.5-flash-preview` - Live API optimized model
- `gemini-2.5-flash-native-audio-preview-09-2025` - Native audio model with advanced features

### System Instructions

Customize the AI assistant's behavior and personality with system instructions:

```typescript
{
  system_instruction: "You are a helpful AI assistant communicating via WebRTC. Be concise and friendly."
}
```

## Response Configuration

### Response Modalities

Choose output format (only one can be selected per session):

- `AUDIO` - Audio responses (24kHz output)
- `TEXT` - Text-only responses

**Note**: You cannot use both AUDIO and TEXT simultaneously in one session.

### Media Resolution

Control the quality of media processing:

- `low` - Lower quality, faster processing
- `medium` - Balanced quality and performance (default)
- `high` - Highest quality, more resource intensive

## Generation Settings

Control the AI's creativity and response characteristics:

### Temperature (0.0 - 2.0)
Default: 1.0

Controls randomness in responses. Higher values make output more creative, lower values make it more focused and deterministic.

### Top P (0.0 - 1.0)
Default: 0.95

Nucleus sampling parameter. Controls diversity via nucleus sampling.

### Top K (1 - 100)
Default: 40

Limits the number of highest probability tokens to consider.

### Max Output Tokens
Default: 8192

Maximum number of tokens in the response.

### Additional Parameters

- `presence_penalty` - Penalizes tokens based on their presence
- `frequency_penalty` - Penalizes tokens based on their frequency
- `stop_sequences` - Array of sequences that stop generation

## Voice Configuration

### Available Voices

Choose from 8 different voice presets:

- `Puck` - Energetic and playful
- `Charon` - Deep and authoritative
- `Kore` - Warm and friendly
- `Fenrir` - Strong and confident
- `Aoede` - Melodic and expressive
- `Leda` - Calm and soothing
- `Orus` - Professional and clear
- `Zephyr` - Light and breezy

### Preemptive Interruption

Default: true

Enables the model to naturally handle interruptions in conversation, allowing for more natural dialogue flow.

## Speech Configuration

### Language Code

Set the language using BCP-47 format:

- `en-US` - English (US)
- `en-GB` - English (UK)
- `de-DE` - German
- `fr-FR` - French
- `ja-JP` - Japanese
- `es-ES` - Spanish

**Note**: Native audio models automatically detect language.

### Voice Activity Detection (VAD)

Fine-tune speech detection parameters:

#### Start of Speech Sensitivity (0.0 - 1.0)
Default: 0.5

How quickly the system detects the start of speech. Higher values are more sensitive.

#### End of Speech Sensitivity (0.0 - 1.0)
Default: 0.5

How quickly the system detects the end of speech. Higher values are more sensitive.

#### Prefix Padding (milliseconds)
Default: 300

Amount of audio to include before detected speech starts.

#### Silence Duration (milliseconds)
Default: 1000

Duration of silence before considering speech has ended.

## Transcription Settings

### Input Audio Transcription

Enable to receive text transcriptions of user's audio input.

### Output Audio Transcription

Enable to receive text transcriptions of the model's audio output.

**Use Case**: Useful for debugging, logging, or providing subtitles.

## Native Audio Features

These features are only available with native audio models (e.g., `gemini-2.5-flash-native-audio-preview-09-2025`).

### Affective Dialog

Enables emotion-aware dialogue where the model can detect and respond to emotional context in the user's voice.

### Proactive Audio

Allows the model to proactively provide information or ask questions without explicit user prompts.

### Thinking Budget (seconds)

Default: 5

Time allocated for the model to "think" before responding. Set to 0 to disable thinking time.

**Range**: 0-30 seconds

## Session Management

### Context Window Compression

Enables automatic compression of the conversation context to extend session duration.

#### Compression Token Threshold

Default: 100,000

Number of tokens before compression is triggered.

**Note**: Extends sessions beyond the default 15-minute limit for audio-only sessions.

### Session Resumption

Allows reconnection to existing sessions after disconnection.

**Validity**: Resumption handles remain valid for 2 hours after session termination.

## Tools & Function Calling

### Built-in Tools

#### Google Search

Enable real-time web search integration to reduce hallucinations and provide up-to-date information.

```typescript
{
  enable_google_search: true
}
```

#### Code Execution

Enable Python code generation and execution for computations.

```typescript
{
  enable_code_execution: true
}
```

**Note**: Only available in `gemini-live-2.5-flash-preview` and native audio models.

### Function Calling Behavior

#### Blocking vs Non-Blocking

- `BLOCKING` - Model waits for function results before continuing
- `NON_BLOCKING` - Model continues while function executes asynchronously

#### Response Scheduling

Controls how function results are communicated:

- `INTERRUPT` - Immediately notify about results
- `WHEN_IDLE` - Wait until model finishes current task
- `SILENT` - Store knowledge for later use without interrupting

### Custom Function Declarations

Define custom functions the model can call:

```typescript
{
  function_declarations: [
    {
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string" }
        }
      }
    }
  ]
}
```

## Frontend Usage

### Applying Configuration

The React frontend provides a comprehensive UI for all configuration options:

```typescript
import { GeminiConfigPanel } from './GeminiConfig';
import { GeminiConfig } from '@webrtc-enterprise/client';

function App() {
  const handleApplyConfig = async (config: GeminiConfig) => {
    await client.sendGeminiConfig(config);
  };

  return <GeminiConfigPanel onApply={handleApplyConfig} />;
}
```

### Programmatic Configuration

You can also configure Gemini programmatically:

```typescript
const config: GeminiConfig = {
  model_name: 'gemini-2.0-flash-exp',
  system_instruction: 'You are a helpful assistant.',
  response_modalities: ['AUDIO'],
  generation_config: {
    temperature: 0.7,
    top_p: 0.9,
    max_output_tokens: 4096,
  },
  voice_config: {
    voice_name: 'Puck',
    preemptive_interruption: true,
  },
  tool_config: {
    enable_google_search: true,
    enable_code_execution: false,
  },
};

await client.sendGeminiConfig(config);
```

## Session Limits

### Duration Limits

- **Audio-only sessions**: 15 minutes (without compression)
- **Audio-video sessions**: 2 minutes (without compression)
- **WebSocket connection**: ~10 minutes

Use context window compression to extend sessions beyond these limits.

### Context Window Sizes

- **Native audio models**: 128k tokens
- **Other models**: 32k tokens

## Best Practices

1. **Start with defaults**: The default configuration works well for most use cases
2. **Test voice options**: Try different voices to find the best fit for your application
3. **Tune VAD carefully**: VAD settings significantly impact conversation flow
4. **Enable compression for long sessions**: Essential for sessions longer than 15 minutes
5. **Use native audio models for emotion**: Only native audio models support affective dialog
6. **Enable search for factual queries**: Google Search reduces hallucinations
7. **Monitor token usage**: Keep track of context window usage for long conversations

## Troubleshooting

### Audio Quality Issues

- Increase `media_resolution` to `high`
- Adjust VAD `prefix_padding_ms` if speech is cut off
- Check network bandwidth

### Response Delays

- Reduce `thinking_budget`
- Lower `temperature` for faster, more predictable responses
- Use `BLOCKING` function behavior for critical operations

### Session Timeouts

- Enable `context_window_compression`
- Implement session resumption for critical applications
- Monitor session duration and warn users

## API Reference

For complete API documentation, see:
- [Gemini Live API Documentation](https://ai.google.dev/gemini-api/docs/live)
- [Live API Guide](https://ai.google.dev/gemini-api/docs/live-guide)
- [Tools Documentation](https://ai.google.dev/gemini-api/docs/live-tools)
- [Session Management](https://ai.google.dev/gemini-api/docs/live-session)
