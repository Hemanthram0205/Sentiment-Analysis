/**
 * NRC Word-Emotion Association Lexicon (subset)
 * Based on Saif Mohammad & Peter Turney — NRC Canada
 *
 * Each word maps to an array of emotions from:
 * joy | sadness | anger | fear | disgust | surprise | trust | anticipation
 */
const nrcLexicon = {
    // ── A ──
    "abandon": ["fear", "sadness"],
    "abhor": ["anger", "disgust"],
    "abhorrent": ["anger", "disgust"],
    "abject": ["sadness", "fear"],
    "abuse": ["anger", "disgust", "sadness"],
    "accomplish": ["joy", "anticipation", "trust"],
    "achievement": ["joy", "anticipation"],
    "admire": ["joy", "trust"],
    "adore": ["joy", "trust"],
    "adventure": ["anticipation", "joy", "surprise"],
    "afraid": ["fear", "sadness"],
    "aggression": ["anger"],
    "agony": ["sadness", "fear"],
    "alarm": ["fear", "surprise"],
    "alienate": ["sadness", "disgust"],
    "amazing": ["joy", "surprise"],
    "anger": ["anger"],
    "anguish": ["sadness", "fear"],
    "annoy": ["anger", "disgust"],
    "anxiety": ["fear", "sadness"],
    "appalled": ["disgust", "anger", "surprise"],
    "appreciate": ["joy", "trust"],
    "approval": ["joy", "trust"],
    "aspire": ["anticipation", "joy"],
    "astound": ["surprise", "joy"],
    "attack": ["anger", "fear"],
    "awe": ["surprise", "joy", "trust"],
    "awful": ["sadness", "disgust"],

    // ── B ──
    "bad": ["sadness", "disgust"],
    "beautiful": ["joy", "trust"],
    "beloved": ["joy", "trust"],
    "bereave": ["sadness"],
    "bereavement": ["sadness", "fear"],
    "betrayal": ["anger", "sadness", "disgust"],
    "bewildered": ["surprise", "fear"],
    "bliss": ["joy", "trust"],
    "bold": ["anticipation", "trust"],
    "boring": ["sadness", "disgust"],
    "brave": ["anticipation", "trust", "joy"],
    "bravery": ["trust", "anticipation"],

    // ── C ──
    "calm": ["trust", "joy"],
    "catastrophe": ["fear", "sadness", "surprise"],
    "celebrate": ["joy", "anticipation"],
    "chaos": ["fear", "anger", "surprise"],
    "charm": ["joy", "trust"],
    "cheat": ["anger", "disgust", "sadness"],
    "cheerful": ["joy"],
    "comfort": ["joy", "trust"],
    "compassion": ["trust", "sadness", "joy"],
    "confident": ["trust", "anticipation", "joy"],
    "confusion": ["fear", "surprise"],
    "courageous": ["trust", "anticipation"],
    "crime": ["anger", "disgust", "fear"],
    "cruel": ["disgust", "anger", "sadness"],
    "curious": ["anticipation", "surprise", "joy"],

    // ── D ──
    "danger": ["fear", "anticipation"],
    "death": ["sadness", "fear"],
    "deceit": ["disgust", "anger"],
    "defeat": ["sadness", "anger"],
    "depressed": ["sadness"],
    "depression": ["sadness", "fear"],
    "desperate": ["fear", "sadness", "anticipation"],
    "destroy": ["anger", "sadness"],
    "devastated": ["sadness", "surprise"],
    "devoted": ["trust", "joy"],
    "devoted": ["joy", "trust"],
    "dirty": ["disgust"],
    "disappoint": ["sadness", "anger"],
    "disaster": ["fear", "sadness", "surprise"],
    "disgusting": ["disgust"],
    "distress": ["sadness", "fear"],
    "doubt": ["fear", "sadness"],
    "dreadful": ["fear", "disgust"],

    // ── E ──
    "ecstasy": ["joy", "surprise"],
    "effective": ["trust", "anticipation"],
    "empathy": ["trust", "sadness", "joy"],
    "encourage": ["trust", "anticipation", "joy"],
    "enjoy": ["joy", "anticipation"],
    "enlighten": ["surprise", "trust", "anticipation"],
    "enthusiasm": ["joy", "anticipation"],
    "excel": ["joy", "anticipation", "trust"],
    "excited": ["joy", "anticipation", "surprise"],
    "exhausted": ["sadness"],

    // ── F ──
    "fail": ["sadness", "anger"],
    "faithful": ["trust", "joy"],
    "fantastic": ["joy", "surprise"],
    "fear": ["fear"],
    "fearful": ["fear", "sadness"],
    "fierce": ["anger", "anticipation"],
    "forgive": ["trust", "joy"],
    "fraud": ["disgust", "anger"],
    "free": ["joy", "anticipation", "trust"],
    "friendly": ["trust", "joy"],
    "frightened": ["fear", "surprise"],
    "frustrated": ["anger", "sadness"],
    "fun": ["joy", "anticipation"],
    "funny": ["joy", "surprise"],

    // ── G ──
    "gentle": ["trust", "joy"],
    "glad": ["joy"],
    "glory": ["joy", "trust", "anticipation"],
    "good": ["joy", "trust"],
    "graceful": ["joy", "trust"],
    "grateful": ["joy", "trust"],
    "great": ["joy", "anticipation"],
    "grief": ["sadness", "fear"],
    "growth": ["anticipation", "joy", "trust"],
    "guilty": ["sadness", "fear"],

    // ── H ──
    "happiness": ["joy"],
    "happy": ["joy"],
    "harm": ["anger", "sadness", "fear"],
    "hate": ["anger", "disgust"],
    "helpless": ["sadness", "fear"],
    "heroic": ["trust", "joy", "anticipation"],
    "hopeful": ["anticipation", "joy", "trust"],
    "hopeless": ["sadness", "fear"],
    "horrible": ["disgust", "fear", "sadness"],
    "hostile": ["anger", "disgust"],
    "humble": ["trust", "joy"],
    "hurt": ["sadness", "anger"],

    // ── I ──
    "ignorant": ["anger", "disgust"],
    "injustice": ["anger", "sadness", "disgust"],
    "inspire": ["joy", "anticipation", "trust"],
    "insult": ["anger", "disgust", "sadness"],

    // ── J ──
    "jealous": ["anger", "sadness", "disgust"],
    "joyful": ["joy"],
    "joyous": ["joy", "surprise"],
    "jubilant": ["joy", "surprise"],

    // ── K ──
    "kind": ["trust", "joy"],
    "kindness": ["trust", "joy"],

    // ── L ──
    "lazy": ["disgust", "sadness"],
    "lonely": ["sadness"],
    "love": ["joy", "trust", "anticipation"],
    "loyal": ["trust", "joy"],

    // ── M ──
    "magnificent": ["joy", "surprise", "trust"],
    "manipulate": ["anger", "disgust"],
    "melancholy": ["sadness"],
    "miracle": ["surprise", "joy", "trust"],
    "miserable": ["sadness"],
    "motivated": ["anticipation", "joy", "trust"],
    "mourning": ["sadness", "fear"],

    // ── N ──
    "neglect": ["sadness", "anger", "disgust"],
    "nervous": ["fear"],
    "nightmare": ["fear", "sadness"],

    // ── O ──
    "optimistic": ["anticipation", "joy", "trust"],
    "outstanding": ["joy", "surprise", "trust"],
    "overwhelmed": ["fear", "surprise", "sadness"],

    // ── P ──
    "panic": ["fear", "surprise"],
    "passionate": ["joy", "anticipation", "trust"],
    "patience": ["trust", "anticipation"],
    "peaceful": ["joy", "trust"],
    "pessimistic": ["sadness", "fear"],
    "powerful": ["trust", "anticipation", "joy"],
    "prejudice": ["disgust", "anger"],
    "pride": ["joy", "trust", "anticipation"],
    "purposeful": ["anticipation", "trust"],

    // ── R ──
    "rage": ["anger"],
    "regret": ["sadness"],
    "rejected": ["sadness", "anger"],
    "resilient": ["trust", "anticipation"],
    "respect": ["trust", "joy"],
    "restore": ["trust", "anticipation", "joy"],
    "ruin": ["sadness", "anger", "disgust"],

    // ── S ──
    "sad": ["sadness"],
    "sadness": ["sadness"],
    "selfish": ["disgust", "anger"],
    "shame": ["sadness", "fear", "disgust"],
    "shocked": ["surprise", "fear"],
    "sincere": ["trust"],
    "sorrow": ["sadness"],
    "stable": ["trust"],
    "stress": ["fear", "anger", "sadness"],
    "struggle": ["sadness", "fear", "anger"],
    "success": ["joy", "trust", "anticipation"],
    "suffering": ["sadness", "fear"],
    "support": ["trust", "joy"],
    "surprise": ["surprise"],

    // ── T ──
    "terror": ["fear"],
    "thankful": ["joy", "trust"],
    "thoughtful": ["trust", "anticipation"],
    "toxic": ["disgust", "anger", "sadness"],
    "tragedy": ["sadness", "fear"],
    "trust": ["trust"],
    "truthful": ["trust"],

    // ── U ──
    "uncertain": ["fear", "anticipation"],
    "unfair": ["anger", "sadness", "disgust"],
    "upset": ["sadness", "anger"],

    // ── V ──
    "valuable": ["trust", "anticipation"],
    "victorious": ["joy", "anticipation", "trust"],
    "violence": ["anger", "fear", "disgust"],
    "vulnerable": ["fear", "sadness"],

    // ── W ──
    "warmth": ["joy", "trust"],
    "wonderful": ["joy", "surprise", "trust"],
    "worry": ["fear", "sadness"],
    "worthless": ["sadness", "disgust"],

    // ── Z ──
    "zealous": ["anticipation", "anger"]
};

// Emotion metadata: emoji, color (CSS), label
const emotionMeta = {
    joy: { emoji: "😊", color: "#f9d71c", label: "Joy" },
    sadness: { emoji: "😢", color: "#74b9ff", label: "Sadness" },
    anger: { emoji: "😡", color: "#ff4757", label: "Anger" },
    fear: { emoji: "😨", color: "#a29bfe", label: "Fear" },
    disgust: { emoji: "🤢", color: "#55efc4", label: "Disgust" },
    surprise: { emoji: "😮", color: "#fd79a8", label: "Surprise" },
    trust: { emoji: "🤝", color: "#00cec9", label: "Trust" },
    anticipation: { emoji: "⏳", color: "#e17055", label: "Anticipation" }
};

/**
 * analyzeEmotions(text)
 * Returns { scores, dominant, wordsByEmotion, totalEmotionWords }
 */
function analyzeEmotions(text) {
    const words = text.toLowerCase().match(/\b[\w']+\b/g) || [];
    const scores = { joy: 0, sadness: 0, anger: 0, fear: 0, disgust: 0, surprise: 0, trust: 0, anticipation: 0 };
    const wordsByEmotion = { joy: [], sadness: [], anger: [], fear: [], disgust: [], surprise: [], trust: [], anticipation: [] };

    words.forEach(word => {
        const emotions = nrcLexicon[word];
        if (emotions) {
            emotions.forEach(e => {
                scores[e]++;
                if (!wordsByEmotion[e].includes(word)) wordsByEmotion[e].push(word);
            });
        }
    });

    const total = Object.values(scores).reduce((a, b) => a + b, 0);
    const dominant = total > 0 ? Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0] : null;

    return { scores, dominant, wordsByEmotion, total };
}
