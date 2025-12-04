/**
 * Symphonic Joules: Event-to-Music Translation Engine
 * 
 * This schema defines how Pond metrics become musical artifacts across
 * three formats (ABC, MusicXML, JSON). It's the bridge between infrastructure
 * and expression.
 */

// ============================================================================
// PART 1: EVENT SCHEMA (from Pond/CodeQL/System Monitors)
// ============================================================================

const SystemEvent = {
  // Unique identifier (for composition tracking)
  eventId: "event-2025-11-13-cli-codeql-001",
  
  // When it happened (ISO 8601)
  timestamp: "2025-11-13T15:42:33.000Z",
  
  // What triggered the event
  eventType: "security_alert", // or: "recovery", "spike", "deployment", "error", "uptime_milestone"
  
  // Where it happened (system/repo/service)
  subsystem: {
    category: "repository", // or: "service", "database", "network", "ci_cd"
    name: "Pond-Glyphs/cli",
    owner: "Pond-Glyphs",
  },
  
  // Severity/intensity (0.0 to 1.0, influences dynamics)
  severity: 0.7, // 0 = negligible, 1.0 = critical
  
  // Alert-specific metadata
  metadata: {
    tool: "CodeQL", // CodeQL, dependabot, monitor, etc.
    alertId: 5,
    alertCount: 7,
    category: "high-severity",
    description: "Potential SQL injection vulnerability",
    affectedComponent: "query_builder.js",
  },
  
  // System health at time of event
  systemHealth: {
    cpuUsage: 0.65,
    memoryUsage: 0.52,
    requestLatency: 245, // ms
    errorRate: 0.08,
    coherence: 0.72, // B_Harmonic score
  },
  
  // Trend context (is this improving or worsening?)
  trend: "worsening", // or: "improving", "stable"
  
  // Time-of-day context (influences rhythm)
  timeOfDay: "afternoon", // morning, afternoon, evening, night
};

// ============================================================================
// PART 2: MUSICAL MAPPING RULES
// ============================================================================

const MusicalMappingRules = {
  // EVENT TYPE â MUSICAL KEY (tonal center of the composition)
  eventTypeToKey: {
    security_alert: "A", // A minor for danger
    recovery: "C", // C major for resolution
    spike: "G", // G major for urgency/energy
    deployment: "D", // D major for action
    error: "E", // E minor for dysfunction
    uptime_milestone: "F", // F major for stability
    performance_degradation: "B", // B minor for dissonance
  },
  
  // SEVERITY â CHORD QUALITY
  severityToChord: [
    { range: [0.0, 0.2], chord: "major", name: "Minor concern" },
    { range: [0.2, 0.4], chord: "minor7", name: "Noticeable" },
    { range: [0.4, 0.6], chord: "sus4", name: "Watch closely" },
    { range: [0.6, 0.8], chord: "diminished", name: "Serious" },
    { range: [0.8, 1.0], chord: "diminished7", name: "Critical" },
  ],
  
  // SEVERITY â DYNAMIC MARKING (volume/intensity)
  severityToDynamic: [
    { range: [0.0, 0.2], dynamic: "ppp", musicXML: "ppp" }, // pianississimo
    { range: [0.2, 0.4], dynamic: "pp", musicXML: "pp" },   // pianissimo
    { range: [0.4, 0.6], dynamic: "mp", musicXML: "mp" },   // mezzo-piano
    { range: [0.6, 0.8], dynamic: "f", musicXML: "f" },     // forte
    { range: [0.8, 1.0], dynamic: "fff", musicXML: "fff" }, // fortississimo
  ],
  
  // TIME OF DAY â RHYTHMIC SUBDIVISION
  timeOfDayToRhythm: {
    morning: { subdivision: "1/4", tempoModifier: 1.0, feel: "measured" },
    afternoon: { subdivision: "1/8", tempoModifier: 1.2, feel: "active" },
    evening: { subdivision: "1/16", tempoModifier: 1.4, feel: "frantic" },
    night: { subdivision: "1/32", tempoModifier: 1.6, feel: "critical" },
  },
  
  // SUBSYSTEM CATEGORY â INSTRUMENT VOICE (for polyphony)
  subsystemToVoice: {
    repository: { instrument: "strings", voice: "violin", midiChannel: 0 },
    service: { instrument: "brass", voice: "trumpet", midiChannel: 1 },
    database: { instrument: "woodwind", voice: "cello", midiChannel: 2 },
    network: { instrument: "percussion", voice: "timpani", midiChannel: 3 },
    ci_cd: { instrument: "organ", voice: "bassoon", midiChannel: 4 },
  },
  
  // COHERENCE SCORE â ARTICULATION
  coherenceToArticulation: [
    { range: [0.0, 0.3], articulation: "staccato", symbol: "." },
    { range: [0.3, 0.6], articulation: "normal", symbol: "" },
    { range: [0.6, 0.85], articulation: "legato", symbol: "-" },
    { range: [0.85, 1.0], articulation: "sustain", symbol: "_" },
  ],
  
  // TREND â MELODIC CONTOUR
  trendToContour: {
    improving: { direction: "ascending", intervalPattern: [2, 2, 1] }, // moving up
    stable: { direction: "flat", intervalPattern: [0, 0, 0] }, // static
    worsening: { direction: "descending", intervalPattern: [-2, -2, -1] }, // moving down
  },
};

// ============================================================================
// PART 3: TRANSLATION FUNCTION
// ============================================================================

function translateEventToMusic(event) {
  // Step 1: Determine key based on event type
  const key = MusicalMappingRules.eventTypeToKey[event.eventType] || "C";
  
  // Step 2: Map severity to chord quality and dynamic
  const severityRange = MusicalMappingRules.severityToChord.find(
    (c) => event.severity >= c.range[0] && event.severity < c.range[1]
  );
  const chord = severityRange?.chord || "major";
  const chordName = severityRange?.name || "Unknown";
  
  const dynamicRange = MusicalMappingRules.severityToDynamic.find(
    (d) => event.severity >= d.range[0] && event.severity < d.range[1]
  );
  const dynamic = dynamicRange?.dynamic || "mp";
  const musicXMLDynamic = dynamicRange?.musicXML || "mp";
  
  // Step 3: Map time of day to rhythm
  const rhythmData = MusicalMappingRules.timeOfDayToRhythm[event.timeOfDay] || 
                     MusicalMappingRules.timeOfDayToRhythm.afternoon;
  
  // Step 4: Map subsystem to voice
  const voiceData = MusicalMappingRules.subsystemToVoice[event.subsystem.category] ||
                    MusicalMappingRules.subsystemToVoice.repository;
  
  // Step 5: Map coherence to articulation
  const articulationRange = MusicalMappingRules.coherenceToArticulation.find(
    (a) => event.systemHealth.coherence >= a.range[0] && 
           event.systemHealth.coherence < a.range[1]
  );
  const articulation = articulationRange?.articulation || "normal";
  const articulationSymbol = articulationRange?.symbol || "";
  
  // Step 6: Calculate tempo from time of day and error rate
  const baseTempoMap = { morning: 80, afternoon: 100, evening: 120, night: 140 };
  const baseTempo = baseTempoMap[event.timeOfDay] || 100;
  const tempo = Math.round(baseTempo * (1 + event.systemHealth.errorRate));
  
  // Step 7: Generate pitch (based on severity and coherence)
  const basePitch = 60 + (event.severity * 24); // C4 to C6 range
  const coherencePitch = basePitch * (0.8 + event.systemHealth.coherence * 0.4);
  
  // Step 8: Calculate note duration
  const rhythmSubdivision = rhythmData.subdivision;
  const noteDuration = rhythmSubdivision; // "1/4", "1/8", etc.
  
  // Step 9: Trend direction
  const contourData = MusicalMappingRules.trendToContour[event.trend] || 
                      MusicalMappingRules.trendToContour.stable;
  
  return {
    // Musical attributes
    musical: {
      key,
      chord,
      dynamic,
      musicXMLDynamic,
      tempo,
      rhythm: rhythmSubdivision,
      pitch: Math.round(coherencePitch),
      pitchNote: midiToNoteName(Math.round(coherencePitch)),
      articulation,
      articulation_symbol: articulationSymbol,
      voice: voiceData.instrument,
      instrument: voiceData.voice,
      midiChannel: voiceData.midiChannel,
      contour: contourData.direction,
      intervalPattern: contourData.intervalPattern,
    },
    
    // Event metadata (preserved for archival)
    event: {
      eventId: event.eventId,
      timestamp: event.timestamp,
      eventType: event.eventType,
      subsystem: event.subsystem.name,
      severity: event.severity,
      severityLevel: chordName,
      systemHealth: event.systemHealth,
      trend: event.trend,
    },
    
    // Emotional interpretation
    emotional: {
      state: getEmotionalState(event),
      intensity: event.severity,
      coherence: event.systemHealth.coherence,
      stability: 1 - event.systemHealth.errorRate,
    },
  };
}

// ============================================================================
// PART 4: HELPER FUNCTIONS
// ============================================================================

function midiToNoteName(midi) {
  const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const octave = Math.floor(midi / 12) - 1;
  const noteIndex = midi % 12;
  return notes[noteIndex] + octave;
}

function getEmotionalState(event) {
  const coherence = event.systemHealth.coherence;
  const errorRate = event.systemHealth.errorRate;
  const severity = event.severity;
  
  if (coherence > 0.8 && errorRate < 0.1 && severity < 0.3) return "flow";
  if (coherence > 0.6 && errorRate < 0.2 && severity < 0.5) return "stable";
  if (coherence > 0.4 && severity < 0.7) return "uncertain";
  if (severity > 0.7 || errorRate > 0.3) return "distressed";
  return "chaotic";
}

// ============================================================================
// PART 5: EXAMPLE USAGE
// ============================================================================

const exampleEvent = {
  eventId: "event-2025-11-13-cli-codeql-001",
  timestamp: "2025-11-13T15:42:33.000Z",
  eventType: "security_alert",
  subsystem: {
    category: "repository",
    name: "Pond-Glyphs/cli",
    owner: "Pond-Glyphs",
  },
  severity: 0.75,
  metadata: {
    tool: "CodeQL",
    alertId: 5,
    alertCount: 7,
    category: "high-severity",
  },
  systemHealth: {
    cpuUsage: 0.65,
    memoryUsage: 0.52,
    requestLatency: 245,
    errorRate: 0.08,
    coherence: 0.72,
  },
  trend: "worsening",
  timeOfDay: "afternoon",
};

const translation = translateEventToMusic(exampleEvent);

console.log("=== SYMPHONIC JOULES EVENT TRANSLATION ===");
console.log("\nð Input Event:");
console.log(`  Type: ${exampleEvent.eventType} (${exampleEvent.subsystem.name})`);
console.log(`  Severity: ${exampleEvent.severity} (${translation.event.severityLevel})`);
console.log(`  Coherence: ${exampleEvent.systemHealth.coherence}`);

console.log("\nðµ Musical Translation:");
console.log(`  Key: ${translation.musical.key}`);
console.log(`  Chord: ${translation.musical.chord}`);
console.log(`  Dynamic: ${translation.musical.dynamic}`);
console.log(`  Tempo: ${translation.musical.tempo} BPM`);
console.log(`  Pitch: ${translation.musical.pitchNote}`);
console.log(`  Articulation: ${translation.musical.articulation}`);
console.log(`  Voice: ${translation.musical.voice} (${translation.musical.instrument})`);

console.log("\nð­ Emotional State:");
console.log(`  State: ${translation.emotional.state}`);
console.log(`  Intensity: ${translation.emotional.intensity}`);

// ============================================================================
// PART 6: OUTPUT GENERATORS (ABC, MusicXML, JSON)
// ============================================================================

/**
 * Generate ABC notation from translated event
 */
function generateABCFromEvent(translation) {
  const abc = `X:1
T:${translation.event.eventType} - ${translation.event.subsystem}
C:Pond Archivist
D:${new Date(translation.event.timestamp).toLocaleDateString()}
L:${translation.musical.rhythm}
M:4/4
K:${translation.musical.key}
%% dynamic ${translation.musical.musicXMLDynamic}
${translation.musical.pitchNote}${translation.musical.articulation_symbol} `;
  
  return abc;
}

/**
 * Generate MusicXML from translated event
 */
function generateMusicXMLFromEvent(translation) {
  const xml = `<?xml version="1.0"?>
<note>
  <pitch>
    <step>${translation.musical.pitchNote[0]}</step>
    <octave>${translation.musical.pitchNote.slice(-1)}</octave>
  </pitch>
  <duration>4</duration>
  <dynamics>${translation.musical.musicXMLDynamic}</dynamics>
  <articulations>${translation.musical.articulation}</articulations>
</note>`;
  
  return xml;
}

/**
 * Generate JSON (full preservation)
 */
function generateJSONFromEvent(translation) {
  return JSON.stringify(translation, null, 2);
}

// Export for use in other modules
module.exports = {
  SystemEvent,
  MusicalMappingRules,
  translateEventToMusic,
  generateABCFromEvent,
  generateMusicXMLFromEvent,
  generateJSONFromEvent,
};