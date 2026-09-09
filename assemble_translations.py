# -*- coding: utf-8 -*-
import json, os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trans_en_hi_bho import en, hi, bho
from trans_pa_bn_gu import pa, bn, gu
from trans_mr_ta_te_kn import mr, ta, te, kn

all_langs = {
    "en": en,
    "hi": hi,
    "bho": bho,
    "pa": pa,
    "bn": bn,
    "gu": gu,
    "mr": mr,
    "ta": ta,
    "te": te,
    "kn": kn
}

# Verify parity
en_keys = set(en.keys())
print(f"Master EN key count: {len(en_keys)}")
all_valid = True
for code, d in all_langs.items():
    cur_keys = set(d.keys())
    missing = en_keys - cur_keys
    extra = cur_keys - en_keys
    if missing:
        print(f"Error: {code} missing {len(missing)} keys: {missing}")
        all_valid = False
    if extra:
        print(f"Error: {code} has {len(extra)} extra keys: {extra}")
        all_valid = False
    if not missing and not extra:
        print(f"✓ {code}: 100% parity ({len(cur_keys)} keys)")

if not all_valid:
    print("Aborting assembly due to parity errors.")
    sys.exit(1)

js_content = """// SahakarConnect Universal 10-Language Translation Engine & Voice-to-Text Controller

const SPEECH_LANG_MAP = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'bho': 'hi-IN',
    'pa': 'pa-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'mr': 'mr-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'kn': 'kn-IN'
};

const stateLanguages = {
    "en": "English",
    "hi": "हिन्दी",
    "bho": "भोजपुरी",
    "pa": "ਪੰਜਾਬੀ",
    "bn": "বাংলা",
    "gu": "ગુજરાતી",
    "mr": "मराठी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "kn": "ಕನ್ನಡ"
};

const portalTranslations = """ + json.dumps(all_langs, indent=4, ensure_ascii=False) + """;

function getI18n(key, fallback = "") {
    const lang = localStorage.getItem('sahakar_lang') || 'en';
    if (portalTranslations[lang] && portalTranslations[lang][key]) {
        return portalTranslations[lang][key];
    }
    if (portalTranslations['en'] && portalTranslations['en'][key]) {
        return portalTranslations['en'][key];
    }
    return fallback || key;
}

function applyLanguage(lang) {
    if (!lang || !portalTranslations[lang]) lang = 'en';
    localStorage.setItem('sahakar_lang', lang);

    const selectEls = document.querySelectorAll('#globalLangSelect');
    selectEls.forEach(el => { el.value = lang; });

    const dict = portalTranslations[lang] || portalTranslations['en'];

    // Update all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        if (dict[k]) {
            el.innerHTML = dict[k];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const k = el.getAttribute('data-i18n-placeholder');
        if (dict[k]) {
            el.placeholder = dict[k];
        }
    });
}

// Voice-to-Text Recognition in all 10 Languages
function startVoiceRecognition(inputId, statusCallback = null) {
    const currentLang = localStorage.getItem('sahakar_lang') || 'en';
    const speechCode = SPEECH_LANG_MAP[currentLang] || 'en-IN';

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Voice speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = speechCode;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    if (statusCallback) statusCallback('Listening... (speak in ' + (stateLanguages[currentLang] || 'your language') + ')');

    recognition.onstart = () => {
        console.log('Voice recognition started for lang:', speechCode);
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const inputEl = document.getElementById(inputId);
        if (inputEl) {
            inputEl.value = transcript;
            inputEl.focus();
        }
        if (statusCallback) statusCallback('Captured: "' + transcript + '"');
    };

    recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        if (statusCallback) statusCallback('Voice error: ' + event.error);
    };

    recognition.onend = () => {
        setTimeout(() => {
            if (statusCallback) statusCallback('');
        }, 3000);
    };

    recognition.start();
}

window.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('sahakar_lang') || 'en';
    applyLanguage(saved);
});
"""

target = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/js/translations.js')
with open(target, 'w', encoding='utf-8') as f:
    f.write(js_content)
print(f"Successfully written {os.path.getsize(target)} bytes to {target}")
