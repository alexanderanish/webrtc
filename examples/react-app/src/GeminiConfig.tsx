import React, { useState } from 'react';
import { GeminiConfig } from '@webrtc-enterprise/client';

interface GeminiConfigPanelProps {
  onApply: (config: GeminiConfig) => void;
}

const VOICE_OPTIONS = ['Puck', 'Charon', 'Kore', 'Fenrir', 'Aoede', 'Leda', 'Orus', 'Zephyr'];
const MODEL_OPTIONS = [
  'gemini-2.0-flash-exp',
  'gemini-live-2.5-flash-preview',
  'gemini-2.5-flash-native-audio-preview-09-2025',
];

export function GeminiConfigPanel({ onApply }: GeminiConfigPanelProps) {
  const [showConfig, setShowConfig] = useState(false);

  // Model Configuration
  const [modelName, setModelName] = useState('gemini-2.0-flash-exp');
  const [systemInstruction, setSystemInstruction] = useState(
    'You are a helpful AI assistant communicating via WebRTC. Be concise and friendly.'
  );

  // Response Configuration
  const [responseModalities, setResponseModalities] = useState<string[]>(['AUDIO']);
  const [mediaResolution, setMediaResolution] = useState<'low' | 'medium' | 'high'>('medium');

  // Generation Config
  const [temperature, setTemperature] = useState(1.0);
  const [topP, setTopP] = useState(0.95);
  const [topK, setTopK] = useState(40);
  const [maxOutputTokens, setMaxOutputTokens] = useState(8192);

  // Voice Config
  const [voiceName, setVoiceName] = useState('Puck');
  const [preemptiveInterruption, setPreemptiveInterruption] = useState(true);

  // Speech Config
  const [languageCode, setLanguageCode] = useState('en-US');

  // VAD Config
  const [startOfSpeechSensitivity, setStartOfSpeechSensitivity] = useState(0.5);
  const [endOfSpeechSensitivity, setEndOfSpeechSensitivity] = useState(0.5);
  const [prefixPaddingMs, setPrefixPaddingMs] = useState(300);
  const [silenceDurationMs, setSilenceDurationMs] = useState(1000);

  // Transcription Config
  const [enableInputTranscription, setEnableInputTranscription] = useState(false);
  const [enableOutputTranscription, setEnableOutputTranscription] = useState(false);

  // Native Audio Config
  const [enableAffectiveDialog, setEnableAffectiveDialog] = useState(false);
  const [enableProactiveAudio, setEnableProactiveAudio] = useState(false);
  const [thinkingBudget, setThinkingBudget] = useState(5);

  // Session Config
  const [enableContextCompression, setEnableContextCompression] = useState(false);
  const [compressionTokenThreshold, setCompressionTokenThreshold] = useState(100000);

  // Tool Config
  const [enableCodeExecution, setEnableCodeExecution] = useState(false);
  const [enableGoogleSearch, setEnableGoogleSearch] = useState(false);
  const [functionBehavior, setFunctionBehavior] = useState<'BLOCKING' | 'NON_BLOCKING'>('BLOCKING');
  const [responseScheduling, setResponseScheduling] = useState<'INTERRUPT' | 'WHEN_IDLE' | 'SILENT'>('INTERRUPT');

  const handleApply = () => {
    const config: GeminiConfig = {
      model_name: modelName,
      system_instruction: systemInstruction,
      response_modalities: responseModalities,
      media_resolution: mediaResolution,
      generation_config: {
        temperature,
        top_p: topP,
        top_k: topK,
        max_output_tokens: maxOutputTokens,
      },
      voice_config: {
        voice_name: voiceName,
        preemptive_interruption: preemptiveInterruption,
      },
      speech_config: {
        language_code: languageCode,
        vad_config: {
          start_of_speech_sensitivity: startOfSpeechSensitivity,
          end_of_speech_sensitivity: endOfSpeechSensitivity,
          prefix_padding_ms: prefixPaddingMs,
          silence_duration_ms: silenceDurationMs,
        },
      },
      transcription_config: {
        enable_input_transcription: enableInputTranscription,
        enable_output_transcription: enableOutputTranscription,
      },
      native_audio_config: {
        enable_affective_dialog: enableAffectiveDialog,
        enable_proactive_audio: enableProactiveAudio,
        thinking_budget: thinkingBudget,
      },
      session_config: {
        enable_context_window_compression: enableContextCompression,
        compression_token_threshold: compressionTokenThreshold,
        enable_session_resumption: false,
      },
      tool_config: {
        enable_automatic_function_calling: true,
        function_behavior: functionBehavior,
        response_scheduling: responseScheduling,
        enable_code_execution: enableCodeExecution,
        enable_google_search: enableGoogleSearch,
        enable_url_context: false,
      },
    };

    onApply(config);
    setShowConfig(false);
  };

  return (
    <div className="gemini-config">
      <button
        className="btn-primary"
        onClick={() => setShowConfig(!showConfig)}
        style={{ marginBottom: '10px' }}
      >
        {showConfig ? 'Hide' : 'Show'} Gemini Configuration
      </button>

      {showConfig && (
        <div className="config-panel">
          <h3>Gemini Live API Configuration</h3>

          {/* Model Configuration */}
          <div className="config-section">
            <h4>Model Configuration</h4>
            <label>
              Model:
              <select value={modelName} onChange={(e) => setModelName(e.target.value)}>
                {MODEL_OPTIONS.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </label>
            <label>
              System Instruction:
              <textarea
                value={systemInstruction}
                onChange={(e) => setSystemInstruction(e.target.value)}
                rows={3}
              />
            </label>
          </div>

          {/* Response Configuration */}
          <div className="config-section">
            <h4>Response Configuration</h4>
            <label>
              Response Modality:
              <select
                value={responseModalities[0]}
                onChange={(e) => setResponseModalities([e.target.value])}
              >
                <option value="AUDIO">Audio</option>
                <option value="TEXT">Text</option>
              </select>
            </label>
            <label>
              Media Resolution:
              <select
                value={mediaResolution}
                onChange={(e) => setMediaResolution(e.target.value as 'low' | 'medium' | 'high')}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
          </div>

          {/* Generation Configuration */}
          <div className="config-section">
            <h4>Generation Settings</h4>
            <label>
              Temperature: {temperature.toFixed(2)}
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
              />
            </label>
            <label>
              Top P: {topP.toFixed(2)}
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
              />
            </label>
            <label>
              Top K: {topK}
              <input
                type="number"
                min="1"
                max="100"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
              />
            </label>
            <label>
              Max Output Tokens:
              <input
                type="number"
                min="100"
                max="100000"
                step="100"
                value={maxOutputTokens}
                onChange={(e) => setMaxOutputTokens(parseInt(e.target.value))}
              />
            </label>
          </div>

          {/* Voice Configuration */}
          <div className="config-section">
            <h4>Voice Settings</h4>
            <label>
              Voice:
              <select value={voiceName} onChange={(e) => setVoiceName(e.target.value)}>
                {VOICE_OPTIONS.map((voice) => (
                  <option key={voice} value={voice}>
                    {voice}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <input
                type="checkbox"
                checked={preemptiveInterruption}
                onChange={(e) => setPreemptiveInterruption(e.target.checked)}
              />
              Enable Preemptive Interruption
            </label>
          </div>

          {/* Speech Configuration */}
          <div className="config-section">
            <h4>Speech Settings</h4>
            <label>
              Language Code:
              <input
                type="text"
                value={languageCode}
                onChange={(e) => setLanguageCode(e.target.value)}
                placeholder="e.g., en-US, de-DE, ja-JP"
              />
            </label>
            <h5>Voice Activity Detection</h5>
            <label>
              Start of Speech Sensitivity: {startOfSpeechSensitivity.toFixed(2)}
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={startOfSpeechSensitivity}
                onChange={(e) => setStartOfSpeechSensitivity(parseFloat(e.target.value))}
              />
            </label>
            <label>
              End of Speech Sensitivity: {endOfSpeechSensitivity.toFixed(2)}
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={endOfSpeechSensitivity}
                onChange={(e) => setEndOfSpeechSensitivity(parseFloat(e.target.value))}
              />
            </label>
            <label>
              Prefix Padding (ms):
              <input
                type="number"
                min="0"
                max="1000"
                step="50"
                value={prefixPaddingMs}
                onChange={(e) => setPrefixPaddingMs(parseInt(e.target.value))}
              />
            </label>
            <label>
              Silence Duration (ms):
              <input
                type="number"
                min="100"
                max="5000"
                step="100"
                value={silenceDurationMs}
                onChange={(e) => setSilenceDurationMs(parseInt(e.target.value))}
              />
            </label>
          </div>

          {/* Transcription Configuration */}
          <div className="config-section">
            <h4>Transcription Settings</h4>
            <label>
              <input
                type="checkbox"
                checked={enableInputTranscription}
                onChange={(e) => setEnableInputTranscription(e.target.checked)}
              />
              Enable Input Audio Transcription
            </label>
            <label>
              <input
                type="checkbox"
                checked={enableOutputTranscription}
                onChange={(e) => setEnableOutputTranscription(e.target.checked)}
              />
              Enable Output Audio Transcription
            </label>
          </div>

          {/* Native Audio Features */}
          <div className="config-section">
            <h4>Native Audio Features</h4>
            <p style={{ fontSize: '0.9em', color: '#666' }}>
              (Only for native audio models)
            </p>
            <label>
              <input
                type="checkbox"
                checked={enableAffectiveDialog}
                onChange={(e) => setEnableAffectiveDialog(e.target.checked)}
              />
              Enable Affective Dialog (Emotion-aware)
            </label>
            <label>
              <input
                type="checkbox"
                checked={enableProactiveAudio}
                onChange={(e) => setEnableProactiveAudio(e.target.checked)}
              />
              Enable Proactive Audio
            </label>
            <label>
              Thinking Budget (seconds): {thinkingBudget}
              <input
                type="number"
                min="0"
                max="30"
                value={thinkingBudget}
                onChange={(e) => setThinkingBudget(parseInt(e.target.value))}
              />
            </label>
          </div>

          {/* Session Management */}
          <div className="config-section">
            <h4>Session Management</h4>
            <label>
              <input
                type="checkbox"
                checked={enableContextCompression}
                onChange={(e) => setEnableContextCompression(e.target.checked)}
              />
              Enable Context Window Compression
            </label>
            {enableContextCompression && (
              <label>
                Compression Token Threshold:
                <input
                  type="number"
                  min="10000"
                  max="200000"
                  step="10000"
                  value={compressionTokenThreshold}
                  onChange={(e) => setCompressionTokenThreshold(parseInt(e.target.value))}
                />
              </label>
            )}
          </div>

          {/* Tools Configuration */}
          <div className="config-section">
            <h4>Tools & Function Calling</h4>
            <label>
              <input
                type="checkbox"
                checked={enableCodeExecution}
                onChange={(e) => setEnableCodeExecution(e.target.checked)}
              />
              Enable Code Execution
            </label>
            <label>
              <input
                type="checkbox"
                checked={enableGoogleSearch}
                onChange={(e) => setEnableGoogleSearch(e.target.checked)}
              />
              Enable Google Search
            </label>
            <label>
              Function Behavior:
              <select
                value={functionBehavior}
                onChange={(e) => setFunctionBehavior(e.target.value as 'BLOCKING' | 'NON_BLOCKING')}
              >
                <option value="BLOCKING">Blocking</option>
                <option value="NON_BLOCKING">Non-Blocking</option>
              </select>
            </label>
            <label>
              Response Scheduling:
              <select
                value={responseScheduling}
                onChange={(e) =>
                  setResponseScheduling(e.target.value as 'INTERRUPT' | 'WHEN_IDLE' | 'SILENT')
                }
              >
                <option value="INTERRUPT">Interrupt</option>
                <option value="WHEN_IDLE">When Idle</option>
                <option value="SILENT">Silent</option>
              </select>
            </label>
          </div>

          <div className="config-actions">
            <button className="btn-primary" onClick={handleApply}>
              Apply Configuration
            </button>
            <button className="btn-secondary" onClick={() => setShowConfig(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <style>{`
        .gemini-config {
          margin: 20px 0;
        }

        .config-panel {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          max-height: 600px;
          overflow-y: auto;
        }

        .config-panel h3 {
          margin-top: 0;
          color: #343a40;
          border-bottom: 2px solid #007bff;
          padding-bottom: 10px;
        }

        .config-section {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          padding: 15px;
          margin-bottom: 15px;
        }

        .config-section h4 {
          margin-top: 0;
          color: #495057;
          font-size: 1.1em;
        }

        .config-section h5 {
          margin: 15px 0 10px 0;
          color: #6c757d;
          font-size: 0.95em;
        }

        .config-section label {
          display: block;
          margin-bottom: 12px;
          color: #495057;
          font-weight: 500;
        }

        .config-section input[type="range"] {
          width: 100%;
          margin-top: 5px;
        }

        .config-section input[type="number"],
        .config-section input[type="text"],
        .config-section select,
        .config-section textarea {
          width: 100%;
          padding: 8px;
          margin-top: 5px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-family: inherit;
        }

        .config-section textarea {
          resize: vertical;
          font-family: inherit;
        }

        .config-section input[type="checkbox"] {
          width: auto;
          margin-right: 8px;
        }

        .config-actions {
          display: flex;
          gap: 10px;
          margin-top: 20px;
          padding-top: 15px;
          border-top: 2px solid #dee2e6;
        }

        .btn-secondary {
          background-color: #6c757d;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1em;
        }

        .btn-secondary:hover {
          background-color: #5a6268;
        }
      `}</style>
    </div>
  );
}
