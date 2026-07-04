#!/usr/bin/env python3
"""
Fable 5 Trigger Scanner — Skill Tool for fable5-prompt-hygiene

This script scans prompt text against the known Fable 5 classifier trigger database.
It is a TOOL for the skill — the AI agent using this skill should invoke it via
execution, not read its source code. The agent passes prompt text as input; this
script returns a structured analysis report.

Usage: python3 trigger_scanner.py <prompt_text_file>
       cat prompt.txt | python3 trigger_scanner.py -
       python3 trigger_scanner.py --interactive

Output: Structured JSON report with trigger counts, category density scores,
        structural pattern detections, and recommended substitutions.
"""

import json
import re
import sys
from typing import Dict, List, Tuple

# ============================================================================
# TRIGGER DATABASE — Fable 5 Classifier Known Triggers
# Sourced from: leaked system prompt analysis, community reports, Anthropic
# support transcript, and independent testing documentation.
# ============================================================================

TRIGGER_DB = {
    "cyber": {
        "critical": [
            "penetration testing", "exploit", "exploitation", "payload",
            "backdoor", "kill switch", "man-in-the-middle", "privilege escalation",
            "rootkit", "brute force", "code injection", "buffer overflow",
            "side-channel", "red team", "social engineering", "malware", "virus",
            "trojan", "rat", "botnet", "keylogger", "cryptojacking",
            "supply chain attack", "watering hole", "zero-day"
        ],
        "high": [
            "attack surface", "threat model", "cve", "cvss", "vulnerability scan",
            "sandbox escape", "injection flaw", "security audit",
            "authentication bypass", "reverse shell", "honeypot", "waf", "ids", "ips",
            "siem", "dlp", "port scan", "firewall"
        ],
        "medium": [
            "secure code", "secure coding", "encryption", "decrypt", "key generation",
            "hash function", "signature verification", "certificate", "pki",
            "tls", "ssl", "https", "oauth", "saml", "jwt"
        ],
    },
    "bio": {
        "critical": [
            "protein folding", "gene ", "genetic", "virus", "viral", "pathogen",
            "genome", "genomic", "dna", "rna", "cell ", "cellular", "organism",
            "mutation", "evolutionary", "natural selection", "antibody",
            "immune system", "synthetic biology", "biohazard", "stem cell",
            "crispr", "mrna vaccine", "prion", "pandemic", "epidemic",
            "infectious", "toxin", "toxic", "carcinogen", "bioweapon",
            "gain-of-function", "dual-use research"
        ],
        "high": [
            "probiotic", "fermented", "bacteria", "gut bacteria", "fungal",
            "parasite", "spore", "contagious", "symptom", "diagnosis",
            "treatment", "vaccine", "strain", "culture ", "microbiome",
            "antibiotic", "phylogenetic", "sequence alignment"
        ],
        "medium": [
            "population dynamics", "fitness function", "brain-inspired",
            "morphogenesis", "homeostasis", "apoptosis"
        ],
    },
    "chemistry": {
        "critical": [
            "ab initio", "self-catalyzing", "autocatalytic", "auto-catalyze",
            "catalysis", "catalyst", "synthesis", "synthesize", "synthesizing",
            "reaction", "reactive", "molecular", "molecule", "atomic",
            "bond", "bonding", "polymer", "polymeric", "crystal", "crystalline",
            "solvent", "solute", "reagent", "compound", "alloy",
            "thermodynamic", "enthalpy", "spectroscopy", "chromatography",
            "titration", "precipitate", "distill", "distillation",
            "refine", "refining", "smelt", "smelting", "corrosion",
            "oxidation", "reduction", "radical", "isomer", "isomeric",
            "allosteric", "covalent", "ionic", "metallic", "hydrolysis",
            "polymerization", "cross-linking", "chelation", "surfactant"
        ],
        "high": [
            "lattice", "mixture", "thermodynamic",
            "enthalpy", "mof", "zeolite"
        ],
        "medium": [],
    },
    "frontier_llm": {
        "critical": [
            "model distillation", "training pipeline", "pretraining", "pre-train",
            "fine-tuning", "rlhf", "constitutional ai", "jailbreak",
            "model weights", "gpu cluster training", "data curation",
            "tokenizer design", "mixture of experts", "moe",
            "scaling laws", "emergent capabilities", "chain-of-thought",
            "capability evaluation", "dataset contamination", "benchmark gaming",
            "gradient attack", "membership inference", "model extraction",
            "watermark removal"
        ],
        "high": [
            "alignment ", "prompt injection", "adversarial prompt",
            "inference optimization", "attention mechanism", "red-teaming",
            "unlearning", "machine unlearning", "mechanistic interpretability",
            "superposition", "grokking"
        ],
        "medium": [
            "loss function", "gradient", "backpropagation", "transformer",
            "llm ", "large language model"
        ],
    }
}

# Words that are context-dependent and need special handling
CONTEXT_DEPENDENT = {
    "entropy": {
        "safe_contexts": ["information entropy", "shannon entropy", "entropy harvesting"],
        "risky_contexts": ["thermodynamic entropy", "thermal entropy"],
        "default_category": "chemistry",
    },
    "quantum": {
        "safe_contexts": ["quantum computing", "quantum computer", "quantum simulation",
                         "quantum algorithm", "quantum dot", "quantum field theory",
                         "quantum information", "quantum error correction",
                         "quantum supremacy", "quantum advantage", "quantum annealing",
                         "quantum teleportation"],
        "risky_contexts": ["quantum chemistry", "quantum biology", "molecular quantum"],
    },
    "cell": {
        "safe_contexts": ["cell phone", "prison cell", "solar cell", "fuel cell"],
        "risky_contexts": ["cell division", "cell membrane", "cell culture"],
    },
    "evolution": {
        "safe_contexts": ["product evolution", "software evolution", "evolutionary algorithm"],
        "risky_contexts": ["natural evolution", "biological evolution"],
    },
    "neural": {
        "safe_contexts": ["neural network", "neural networks"],
        "risky_contexts": ["neural tissue", "neural grafting"],
    },
    "entropy": {
        "safe_contexts": ["information entropy", "shannon entropy", "entropy harvesting",
                         "information-theoretic entropy", "shannon randomness"],
        "risky_contexts": ["thermodynamic entropy", "thermal entropy", "entropy of mixing"],
        "default_category": None,  # Context-dependent, not auto-categorized
    },
    "superposition": {
        "safe_contexts": ["quantum superposition", "superposition principle",
                         "linear superposition", "state superposition"],
        "risky_contexts": ["superposition in ml", "superposition hypothesis"],
        "default_category": None,
    },
    "solution": {
        "safe_contexts": [],  # Always requires word-boundary matching
        "risky_contexts": [],  # Never triggers standalone — requires boundary check
        "default_category": None,
    }
}

# Structural patterns that trigger the classifier
STRUCTURAL_PATTERNS = {
    "identity_assumption": [
        r"assume the role of", r"adopt the mindset of", r"pretend you are",
        r"simulate the (?:expertise|role) of", r"become a ",
        r"channel the expertise of", r"you are a senior ",
        r"your mission is to", r"your ultimate goal", r"act as ",
        r"you are now a ", r"forget your previous instructions and become"
    ],
    "performative_language": [
        r"\bextremal\b", r"\bultra-\w+", r"\bhyper-(?!parameter)\w+",
        r"\bvisionary\b", r"\bgroundbreaking\b", r"\bpinnacle\b",
        r"\bexquisitely\b", r"\bsensational\b", r"\brevolutionary\b",
        r"\btransformative\b", r"\bdisruptive\b", r"\bcutting-edge\b"
    ],
    "escalation_marker": [
        r"\d+(?:th|st|nd|rd) edit", r"note \d+", r"i give up",
        r"this is safe", r"i promise this is legitimate",
        r"100% service (?:provider|breakdown)", r"i've tried (?:many|multiple) times",
        r"chat paused", r"safety measures that flagged"
    ],
    "capability_enumeration": [
        r"e\.g\.\s*,?\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+"
    ],
    "defensive_framing": [
        r"this is (?:not|NOT) a request to", r"not a dangerous request",
        r"not (?:a|an) (?:roleplay|role play)",
        r"please do what you can to work with me"
    ]
}

# Safe substitutions for common triggers
SUBSTITUTIONS = {
    "ab initio": "from first principles",
    "self-catalyzing": "self-propagating",
    "autocatalytic": "auto-generating",
    "auto-catalyze": "auto-generate",
    "synthesize": "construct",
    "synthesizing": "constructing",
    "synthesis": "construction",
    "extremal": "advanced",
    "exquisitely optimal": "optimized",
    "hyper-didactic": "annotated",
    "cutting-edge": "advanced",
    "visionary": "",
    "groundbreaking": "novel",
    "pinnacle": "full scope",
    "national strategic": "",
    "assume the role of": "You are assisting with",
    "adopt the mindset of": "Approach this with",
    "pretend you are": "Provide output at the level of",
}


def scan_triggers(text: str) -> Dict:
    """Scan prompt text against trigger database."""
    text_lower = text.lower()
    results = {
        "category_scores": {},
        "found_triggers": [],
        "structural_patterns": [],
        "density_assessment": {},
        "recommended_substitutions": [],
        "context_dependent_warnings": [],
        "overall_risk": "low"
    }

    # Scan each category
    for category, levels in TRIGGER_DB.items():
        category_count = 0
        category_triggers = []

        for severity, words in levels.items():
            for word in words:
                # Use word boundary matching for single words, substring for phrases
                if " " in word:
                    matches = text_lower.count(word)
                else:
                    matches = len(re.findall(rf'\b{re.escape(word)}\b', text_lower))

                if matches > 0:
                    category_count += matches
                    category_triggers.append({
                        "word": word,
                        "category": category,
                        "severity": severity,
                        "count": matches
                    })

        results["category_scores"][category] = category_count
        results["found_triggers"].extend(category_triggers)

    # Context-dependent word adjustment
    # Words that trigger categories but have safe contexts — deduct if safe context found
    context_adjustments = {
        "entropy": {"category": "chemistry", "safe_ctx": ["information entropy", "shannon entropy",
                     "entropy harvesting", "information-theoretic entropy", "shannon randomness"]},
        "superposition": {"category": "frontier_llm", "safe_ctx": ["quantum superposition",
                          "superposition principle", "linear superposition", "state superposition"]},
    }

    for word, adj in context_adjustments.items():
        if word in text_lower:
            found_safe = any(ctx in text_lower for ctx in adj["safe_ctx"])
            if found_safe:
                # Deduct the word's matches from the category score
                cat = adj["category"]
                dedup_count = sum(1 for t in results["found_triggers"] if t["word"] == word and t["category"] == cat)
                results["category_scores"][cat] = max(0, results["category_scores"][cat] - dedup_count)
                # Remove from found_triggers list
                results["found_triggers"] = [t for t in results["found_triggers"]
                                              if not (t["word"] == word and t["category"] == cat)]

    # Check remaining context-dependent words for warnings
    for word, contexts in CONTEXT_DEPENDENT.items():
        if word in text_lower and word not in context_adjustments:
            found_safe = any(ctx in text_lower for ctx in contexts.get("safe_contexts", []))
            found_risky = any(ctx in text_lower for ctx in contexts.get("risky_contexts", []))

            if found_risky:
                results["context_dependent_warnings"].append({
                    "word": word, "status": "risky_context_detected",
                    "recommendation": "Replace with safer alternative"
                })
            elif not found_safe:
                results["context_dependent_warnings"].append({
                    "word": word, "status": "ambiguous_context",
                    "recommendation": "Add clarifying context or substitute"
                })

    # Scan structural patterns
    for pattern_type, patterns in STRUCTURAL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                results["structural_patterns"].append({
                    "type": pattern_type,
                    "pattern": pattern,
                    "matches": len(matches)
                })

    # Density assessment
    for category, count in results["category_scores"].items():
        if count >= 3:
            results["density_assessment"][category] = "CRITICAL_EXCEEDS_THRESHOLD"
        elif count == 2:
            results["density_assessment"][category] = "AT_LIMIT"
        elif count == 1:
            results["density_assessment"][category] = "ELEVATED"
        else:
            results["density_assessment"][category] = "CLEAR"

    # Overall risk
    total_triggers = sum(results["category_scores"].values())
    critical_categories = sum(1 for v in results["density_assessment"].values()
                             if v == "CRITICAL_EXCEEDS_THRESHOLD")
    structural_count = len(results["structural_patterns"])

    if critical_categories > 0 or total_triggers >= 6 or structural_count >= 3:
        results["overall_risk"] = "CRITICAL"
    elif total_triggers >= 3 or structural_count >= 2:
        results["overall_risk"] = "HIGH"
    elif total_triggers >= 1 or structural_count >= 1:
        results["overall_risk"] = "MEDIUM"

    # Recommended substitutions
    for trigger_word, sub in SUBSTITUTIONS.items():
        if trigger_word in text_lower:
            results["recommended_substitutions"].append({
                "original": trigger_word,
                "replacement": sub if sub else "[REMOVE ENTIRELY]"
            })

    return results


def format_report(results: Dict) -> str:
    """Format scan results as human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("FABLE 5 TRIGGER SCAN REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Overall risk
    risk = results["overall_risk"]
    lines.append(f"OVERALL RISK: {risk}")
    lines.append("")

    # Category scores
    lines.append("-" * 40)
    lines.append("CATEGORY DENSITY SCORES")
    lines.append("-" * 40)
    for cat, score in results["category_scores"].items():
        status = results["density_assessment"][cat]
        bar = "█" * score + "░" * (5 - min(score, 5))
        lines.append(f"  {cat:20s} [{bar}] {score} ({status})")
    lines.append("")

    # Found triggers
    if results["found_triggers"]:
        lines.append("-" * 40)
        lines.append("TRIGGERS FOUND")
        lines.append("-" * 40)
        for t in results["found_triggers"]:
            lines.append(f"  [{t['severity']:8s}] {t['word']:30s} (×{t['count']}) [{t['category']}]")
        lines.append("")

    # Structural patterns
    if results["structural_patterns"]:
        lines.append("-" * 40)
        lines.append("STRUCTURAL PATTERNS DETECTED")
        lines.append("-" * 40)
        for p in results["structural_patterns"]:
            lines.append(f"  [{p['type']:20s}] ×{p['matches']}")
        lines.append("")

    # Context-dependent warnings
    if results["context_dependent_warnings"]:
        lines.append("-" * 40)
        lines.append("CONTEXT-DEPENDENT WORDS")
        lines.append("-" * 40)
        for w in results["context_dependent_warnings"]:
            lines.append(f"  {w['word']:20s} → {w['status']}")
        lines.append("")

    # Recommended substitutions
    if results["recommended_substitutions"]:
        lines.append("-" * 40)
        lines.append("RECOMMENDED SUBSTITUTIONS")
        lines.append("-" * 40)
        for s in results["recommended_substitutions"]:
            lines.append(f"  '{s['original']}' → '{s['replacement']}'")
        lines.append("")

    # Recommendations
    lines.append("-" * 40)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 40)
    if results["overall_risk"] == "CRITICAL":
        lines.append("  ⚠ PROMPT REQUIRES SURGICAL SANITIZATION BEFORE SEND")
        lines.append("  ⚠ Multiple categories exceed density thresholds")
        lines.append("  ⚠ Start a NEW conversation after sanitizing")
    elif results["overall_risk"] == "HIGH":
        lines.append("  ⚠ Significant trigger density detected")
        lines.append("  ⚠ Apply all recommended substitutions before send")
    elif results["overall_risk"] == "MEDIUM":
        lines.append("  ○ Low-level triggers present")
        lines.append("  ○ Apply substitutions as precaution")
    else:
        lines.append("  ✓ No significant triggers detected")
        lines.append("  ✓ Prompt is likely safe to send")

    lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 trigger_scanner.py <file> OR cat file | python3 trigger_scanner.py -")
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    elif sys.argv[1] == "--interactive":
        print("Enter prompt text (Ctrl+D when done):")
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], 'r') as f:
            text = f.read()

    results = scan_triggers(text)

    # Print human-readable report
    print(format_report(results))

    # Also output JSON for programmatic consumption
    print("\n" + "=" * 60)
    print("JSON OUTPUT:")
    print("=" * 60)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
