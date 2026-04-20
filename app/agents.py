"""
Evidence Intelligence System — LLM-Powered Multi-Agent Crime Prediction
Uses Ollama as the LLM backbone for local, self-hosted inference.
"""
import os, json, re, base64
from typing import List, Dict, Any
import requests

# ─── LLM HELPER ─────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")
OLLAMA_TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "mistral")

def _llm_json(prompt: str) -> dict:
    """Call Ollama text model and parse JSON from the response."""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_TEXT_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "num_predict": 256
            },
            timeout=90  # Increased to 90 seconds
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama error: {resp.status_code}")
        text = resp.json().get("response", "").strip()
        # Extract JSON from markdown code blocks if present
        m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if m:
            text = m.group(1).strip()
        parsed = json.loads(text)
        return parsed
    except requests.exceptions.Timeout:
        raise RuntimeError("LLM timeout - model loading or slow system")
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {str(e)[:80]}")

def _llm_vision(prompt: str, image_base64: str) -> dict:
    """Call Ollama vision model (llava) for image/video analysis."""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "format": "json",
                "num_predict": 256
            },
            timeout=120  # Increased to 120 seconds
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama vision error: {resp.status_code}")
        text = resp.json().get("response", "").strip()
        m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if m:
            text = m.group(1).strip()
        return json.loads(text)
    except requests.exceptions.Timeout:
        raise RuntimeError("Vision timeout")
    except Exception as e:
        raise RuntimeError(f"Vision analysis failed: {str(e)[:80]}")


# ─── TRAINING DATA (context for LLM) ────────────────────────────────────────────
TRAINING_DATA = [
    {"fir_text": "A man was found injured in a marketplace at night with a knife nearby and blood on the ground.",
     "location": "market", "time": "22:30", "evidence": ["knife", "blood"], "crime_type": "assault"},
    {"fir_text": "A house was broken into during the afternoon. The lock was damaged and valuables were missing.",
     "location": "residential", "time": "15:00", "evidence": ["broken lock"], "crime_type": "burglary"},
    {"fir_text": "A person was found dead in an alley with multiple stab wounds and a weapon nearby.",
     "location": "alley", "time": "night", "evidence": ["knife", "blood"], "crime_type": "homicide"},
    {"fir_text": "A woman reported her purse stolen in a crowded bus during peak hours.",
     "location": "bus", "time": "18:00", "evidence": [], "crime_type": "theft"},
    {"fir_text": "A store reported missing cash after an armed individual threatened the cashier.",
     "location": "store", "time": "21:00", "evidence": ["gun"], "crime_type": "robbery"},
]
TRAINING_JSON = json.dumps(TRAINING_DATA, indent=2)


# ─── KNOWLEDGE GRAPH ────────────────────────────────────────────────────────────
class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self._build()

    def add_node(self, nid, ntype):
        self.nodes[nid] = {"type": ntype}

    def add_edge(self, src, dst, rel, w=1.0):
        self.edges.append({"src": src, "dst": dst, "rel": rel, "weight": w})

    def get_crime_scores(self, tokens, location, time_period):
        scores = {}
        for e in self.edges:
            for t in tokens:
                if t in e["src"] or t in e["dst"]:
                    for side in ("src", "dst"):
                        if self.nodes.get(e[side], {}).get("type") == "crime":
                            scores[e[side]] = scores.get(e[side], 0) + e["weight"]
        for e in self.edges:
            if location.lower() in e["src"] or location.lower() in e["dst"]:
                for side in ("src", "dst"):
                    if self.nodes.get(e[side], {}).get("type") == "crime":
                        scores[e[side]] = scores.get(e[side], 0) + e["weight"] * 0.5
        if time_period in ("night", "late", "late_night"):
            for c in ("assault", "homicide", "robbery"):
                scores[c] = scores.get(c, 0) + 0.15
        return scores

    def _build(self):
        for c in ("assault","homicide","robbery","burglary","theft","kidnapping","arson","fraud","sexual_assault","vandalism","domestic_violence","cyber_crime","drug_offense"):
            self.add_node(c, "crime")
        for ev in ("knife","gun","blood","broken_lock","cctv","fingerprint","dna","vehicle","drugs","accelerant","rope","mask","crowbar","bat","broken_glass"):
            self.add_node(ev, "evidence")
        for loc in ("market","residential","alley","bus","store","highway","school","park","online","office","hospital","street"):
            self.add_node(loc, "location")
        edges = [
            ("knife","assault",0.8),("knife","homicide",0.9),("gun","robbery",0.9),("gun","homicide",0.85),
            ("blood","assault",0.85),("blood","homicide",0.95),("broken_lock","burglary",0.95),
            ("fingerprint","burglary",0.6),("dna","homicide",0.7),("dna","sexual_assault",0.8),
            ("vehicle","kidnapping",0.6),("vehicle","robbery",0.4),("accelerant","arson",0.95),
            ("rope","kidnapping",0.7),("mask","robbery",0.6),("drugs","drug_offense",0.9),
            ("market","theft",0.7),("market","assault",0.5),("residential","burglary",0.9),
            ("alley","homicide",0.7),("alley","assault",0.6),("bus","theft",0.8),
            ("store","robbery",0.8),("online","fraud",0.95),("online","cyber_crime",0.9),
            ("street","assault",0.5),("street","robbery",0.4),("park","assault",0.4),
            ("office","fraud",0.5),("school","kidnapping",0.5),("highway","robbery",0.5),
        ]
        for s, d, w in edges:
            self.add_edge(s, d, "indicates", w)
        for sample in TRAINING_DATA:
            for ev in sample["evidence"]:
                k = ev.replace(" ", "_").lower()
                if k not in self.nodes:
                    self.add_node(k, "evidence")
                self.add_edge(k, sample["crime_type"], "trained_on", 0.7)

_kg = KnowledgeGraph()


# ─── AGENT 1: FIR ANALYZER (LLM) ────────────────────────────────────────────────
class FIRAnalyzerAgent:
    NAME = "FIR_ANALYZER"

    def analyze(self, fir_text, location, time_str):
        log = [f"Analyzing FIR narrative via LLM"]
        # Simplified prompt for faster Ollama processing
        prompt = f"""Analyze this crime FIR. Extract crime type, keywords, and entities. Return JSON only:
FIR: {fir_text[:200]}
Location: {location}

{{
  "crime_indicators": {{"crime_type": {{"keywords": ["<word1>", "<word2>"], "strength": 0.8}}}},
  "entities": {{"weapon": ["<if_any>"], "biomarker": ["<if_any>"]}},
  "time_period": "night|day|unknown"
}}"""

        try:
            data = _llm_json(prompt)
            ci = data.get("crime_indicators", {})
            log.append(f"LLM detected {len(ci)} indicator(s)")
            ent = data.get("entities", {})
            ent = {k: v for k, v in ent.items() if v}
            return {"agent": self.NAME, "crime_indicators": ci, "entities": ent,
                    "time_period": data.get("time_period", "unknown"), "log": log}
        except Exception as e:
            log.append(f"LLM error: {str(e)[:50]}, using fallback")
            return self._fallback(fir_text, location, time_str, log)

    def _fallback(self, fir_text, location, time_str, log):
        text = fir_text.lower()
        KW = {"homicide":["dead","killed","murder","death","body","stab wounds","found dead"],
              "assault":["injured","attacked","beaten","fight","hurt","wound","assault","hit"],
              "robbery":["robbed","armed","threatened","loot","cash missing","weapon point"],
              "burglary":["broken into","break-in","forced entry","lock damaged","valuables missing"],
              "theft":["stolen","snatched","pickpocket","purse","shoplifting","stole","missing"],
              "kidnapping":["kidnapped","abducted","missing child","taken away","captive"],
              "arson":["fire","burnt","arson","blaze","flames"],
              "fraud":["fraud","scam","otp","cheated","fake","cyber","phishing"],
              "vandalism":["vandalism","damage","graffiti","destroyed"],
              "domestic_violence":["domestic","spouse","husband","wife","family violence"]}
        indicators = {}
        for crime, kws in KW.items():
            m = [k for k in kws if k in text]
            if m:
                indicators[crime] = {"keywords": m, "strength": min(len(m)/3, 1.0)}
        # If nothing matched, do similarity against training data
        if not indicators:
            best_score, best_crime = 0, "theft"
            for sample in TRAINING_DATA:
                s_words = set(sample["fir_text"].lower().split())
                t_words = set(text.split())
                overlap = len(s_words & t_words)
                if overlap > best_score:
                    best_score = overlap
                    best_crime = sample["crime_type"]
            indicators[best_crime] = {"keywords": ["text similarity"], "strength": min(best_score/5, 0.8)}
            indicators["theft"] = {"keywords": ["default fallback"], "strength": 0.2}
        ENT = {"weapon":["knife","gun","pistol","rod","bat","sword","weapon"],
               "vehicle":["car","bike","motorcycle","auto","truck","van"],
               "person":["man","woman","child","boy","girl","person","victim"],
               "biomarker":["blood","dna","fingerprint","bruise","wound","injury"]}
        entities = {}
        for etype, pats in ENT.items():
            found = [p for p in pats if p in text]
            if found:
                entities[etype] = found
        tp = "unknown"
        t = time_str.lower().strip()
        if t in ("night","late","midnight"): tp = "night"
        else:
            try:
                h = int(t.split(":")[0])
                tp = "late_night" if h<6 else "morning" if h<12 else "afternoon" if h<17 else "evening" if h<21 else "night"
            except: pass
        log.append(f"Fallback: {len(indicators)} indicators found")
        return {"agent": self.NAME, "crime_indicators": indicators, "entities": entities, "time_period": tp, "log": log}


# ─── AGENT 2: VISION AGENT (LLM) ────────────────────────────────────────────────
class VisionAgent:
    NAME = "VISION_AGENT"

    def analyze(self, evidence_items):
        log = [f"Processing {len(evidence_items)} evidence item(s)"]
        dets = []
        
        for ev in evidence_items:
            ev_type = ev.get('type', 'text')
            image_base64 = ev.get('image_base64')
            description = ev.get('description', '')
            text_ctx = ev.get('text', '')
            
            if image_base64 and ev_type in ('image', 'video'):
                log.append(f"Analyzing {ev_type} via LLM...")
                prompt = f"""Forensic analysis of {ev_type}. Identify objects and evidence.
Description: {description}

{{
  "detections": [{{"object": "name", "confidence": 0.8, "category": "weapon|biomarker|other", "severity": "high", "linked_crimes": ["crime"]}}]
}}"""
                try:
                    data = _llm_vision(prompt, image_base64)
                    img_dets = data.get('detections', [])
                    dets.extend(img_dets)
                    log.append(f"[VISION] {len(img_dets)} object(s)")
                except Exception as e:
                    log.append(f"Vision error, fallback")
                    dets.extend(self._fallback_text(text_ctx, description, log))
            elif text_ctx or description:
                log.append(f"Text evidence analysis")
                combined_text = f"{description} {text_ctx}".strip()
                prompt = f"""Extract objects: {combined_text}
{{"detections": [{{"object": "name", "confidence": 0.7, "category": "type", "severity": "high", "linked_crimes": ["crime"]}}]}}"""
                try:
                    data = _llm_json(prompt)
                    text_dets = data.get('detections', [])
                    dets.extend(text_dets)
                    log.append(f"[TEXT] {len(text_dets)} item(s)")
                except Exception as e:
                    log.append(f"Fallback text analysis")
                    dets.extend(self._fallback_text(text_ctx, description, log))
        
        if not dets:
            log.append("No detections")
        return {"agent": self.NAME, "detections": dets, "log": log}

    def _fallback_text(self, text_ctx, description, log):
        text = f"{description} {text_ctx}".lower()
        patterns = {
            "knife": ("weapon", "high", ["assault", "homicide"]),
            "gun": ("weapon", "critical", ["robbery", "homicide"]),
            "blood": ("biomarker", "high", ["assault", "homicide"]),
            "broken lock": ("entry_tool", "medium", ["burglary"]),
            "rope": ("other", "high", ["kidnapping"]),
        }
        dets = []
        for obj, (cat, sev, crimes) in patterns.items():
            if obj in text:
                dets.append({"object": obj, "confidence": 0.8, "category": cat, "severity": sev, "linked_crimes": crimes})
        return dets


# ─── AGENT 2B: FORENSIC AGENT (LLM) ────────────────────────────────────────────
class ForensicAgent:
    NAME = "FORENSIC_AGENT"

    def analyze(self, evidence_items, fir_entities):
        log = ["Forensic interpretation"]
        combined = " ".join(f"{e.get('description','')} {e.get('text','')}" for e in evidence_items).strip()
        
        prompt = f"""Forensic analysis: {combined}
Entities: {json.dumps(fir_entities if fir_entities else {})}

Return JSON:
{{"interpretations": [{{"marker": "obj", "interpretation": "meaning", "violence_score": 0.7}}], "violence_score": 0.5, "violence_level": "high"}}"""

        try:
            data = _llm_json(prompt)
            return {"agent": self.NAME, "interpretations": data.get("interpretations", []),
                    "violence_score": data.get("violence_score", 0), "violence_level": data.get("violence_level", "low"), "log": log}
        except Exception as e:
            log.append(f"Fallback analysis")
            return self._fallback(combined, fir_entities, log)

        try:
            data = _llm_json(prompt)
            for i in data.get("interpretations", []):
                log.append(f"[FORENSIC] {i['marker']} → {i['interpretation']}")
            log.append(f"Violence: {data.get('violence_level','unknown')} ({data.get('violence_score',0)})")
            return {"agent": self.NAME, "interpretations": data.get("interpretations", []),
                    "violence_score": data.get("violence_score", 0), "violence_level": data.get("violence_level", "low"), "log": log}
        except Exception as e:
            log.append(f"LLM error: {e}, using fallback")
            return self._fallback(combined, fir_entities, log)

    def _fallback(self, text, entities, log):
        text = text.lower()
        for vals in (entities or {}).values():
            text += " " + " ".join(v.lower() for v in vals)
        RULES = {"blood":(0.9,"Violence indicator"),"knife":(0.85,"Stabbing weapon"),"gun":(0.95,"Firearm"),
                 "broken lock":(0.3,"Forced entry"),"wound":(0.85,"Physical trauma"),"injury":(0.8,"Bodily harm"),
                 "stab":(0.9,"Sharp weapon wound"),"bruise":(0.6,"Blunt force")}
        interps, vtotal, cnt = [], 0, 0
        for m, (vs, interp) in RULES.items():
            if m in text:
                interps.append({"marker":m,"interpretation":interp,"violence_score":vs})
                vtotal += vs; cnt += 1
        avg = round(vtotal/max(cnt,1), 2)
        vl = "critical" if avg>0.7 else "high" if avg>0.5 else "moderate" if avg>0.3 else "low"
        return {"agent":self.NAME,"interpretations":interps,"violence_score":avg,"violence_level":vl,"log":log}


# ─── AGENT 4: KNOWLEDGE GRAPH ───────────────────────────────────────────────────
class KnowledgeGraphAgent:
    NAME = "KNOWLEDGE_GRAPH"

    def analyze(self, tokens, location, time_period):
        log = [f"Querying graph ({len(_kg.nodes)} nodes, {len(_kg.edges)} edges)"]
        scores = _kg.get_crime_scores(tokens, location, time_period)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        log.append(f"Scored {len(scores)} crime type(s)")
        for c, s in ranked[:5]:
            log.append(f"  {c}: {round(s,3)}")
        return {"agent": self.NAME, "graph_scores": dict(ranked), "log": log}


# ─── AGENT 5: INFERENCE ENGINE (LLM) ────────────────────────────────────────────
class InferenceAgent:
    NAME = "INFERENCE_ENGINE"
    LABELS = {"assault":"Violent Physical Assault","homicide":"Homicide / Murder","robbery":"Armed Robbery",
              "burglary":"Burglary / Break-in","theft":"Theft / Larceny","kidnapping":"Kidnapping / Abduction",
              "arson":"Arson / Fire Crime","fraud":"Fraud / Cyber Crime","sexual_assault":"Sexual Assault",
              "vandalism":"Vandalism / Property Damage","domestic_violence":"Domestic Violence",
              "cyber_crime":"Cyber Crime","drug_offense":"Drug Offense"}

    def synthesize(self, fir_text, location, time_str, evidence_text,
                   fir_out, vision_out, forensic_out, kg_out):
        log = ["Synthesizing via LLM"]

        # Simplified synthesis prompt for faster processing
        prompt = f"""Crime prediction based on:
FIR: {fir_text[:150]}
Location: {location}
Evidence: {evidence_text[:100]}

Generate 2-3 likely crimes with probability. JSON only:
{{"scenarios": [{{"crime_type": "Crime Name", "crime_key": "key", "probability": 0.7, "description": "short"}}]}}"""

        try:
            data = _llm_json(prompt)
            scenarios = data.get("scenarios", [])
            for s in scenarios:
                if "crime_type" not in s:
                    s["crime_type"] = s.get("crime_key", "Unknown").replace("_", " ").title()
                if "crime_key" not in s:
                    s["crime_key"] = s["crime_type"].lower().replace(" ", "_").replace("/","")
            if scenarios:
                log.append(f"LLM generated {len(scenarios)} scenario(s)")
                return {"agent": self.NAME, "scenarios": scenarios, "log": log}
        except Exception as e:
            log.append(f"LLM timeout: {str(e)[:40]}")
        
        # Fall back immediately if LLM fails
        log.append("Using fallback analysis")
        return self._fallback(fir_out, vision_out, forensic_out, kg_out, location, fir_out.get("time_period","unknown"), log)

    def _fallback(self, fir_out, vision_out, forensic_out, kg_out, location, time_period, log):
        scores = {}
        for crime, info in fir_out.get("crime_indicators",{}).items():
            scores[crime] = scores.get(crime,0) + info.get("strength",0.3) * 0.30
        for det in vision_out.get("detections",[]):
            for c in det.get("linked_crimes",[]):
                scores[c] = scores.get(c,0) + det.get("confidence",0.5) * 0.25
        gs = kg_out.get("graph_scores",{})
        mx = max(gs.values()) if gs else 1
        for crime, raw in gs.items():
            scores[crime] = scores.get(crime,0) + (raw/max(mx,0.01)) * 0.25
        vs = forensic_out.get("violence_score",0)
        for vc in ("assault","homicide","robbery"):
            if vc in scores: scores[vc] += vs * 0.20
        if not scores:
            scores = {"theft": 0.4, "assault": 0.3, "fraud": 0.2, "burglary": 0.1}
        total = sum(scores.values()) or 1
        probs = {k: round(v/total,3) for k,v in scores.items()}
        ranked = sorted(probs.items(), key=lambda x:x[1], reverse=True)
        scenarios = []
        for crime, prob in ranked:
            if prob < 0.03: continue
            scenarios.append({
                "crime_type": self.LABELS.get(crime, crime.replace("_"," ").title()),
                "crime_key": crime, "probability": prob,
                "description": f"Possible {crime.replace('_',' ')} scenario at {location}",
                "reasoning": f"Based on FIR analysis, evidence correlation, and knowledge graph scoring"
            })
        log.append(f"Fallback generated {len(scenarios)} scenarios")
        return {"agent": self.NAME, "scenarios": scenarios, "log": log}


# ─── AGENT 6: ORCHESTRATOR ──────────────────────────────────────────────────────
class OrchestratorAgent:
    NAME = "ORCHESTRATOR"

    def __init__(self):
        self.fir_agent = FIRAnalyzerAgent()
        self.vision_agent = VisionAgent()
        self.forensic_agent = ForensicAgent()
        self.kg_agent = KnowledgeGraphAgent()
        self.inference_agent = InferenceAgent()

    def run_pipeline(self, fir_text, location, time_str, evidence):
        pipeline_log = [{"agent": self.NAME, "action": "Pipeline initiated", "status": "running"}]
        agent_outputs = {}

        # Stage 1: FIR
        pipeline_log.append({"agent":"FIR_ANALYZER","action":"Extracting from FIR narrative via LLM","status":"running"})
        fir_out = self.fir_agent.analyze(fir_text, location, time_str)
        agent_outputs["fir_analyzer"] = fir_out
        pipeline_log.append({"agent":"FIR_ANALYZER","action":f"Found {len(fir_out['crime_indicators'])} indicator(s)","status":"done"})

        # Stage 2: Vision
        pipeline_log.append({"agent":"VISION_AGENT","action":"Scanning evidence objects via LLM+YOLO","status":"running"})
        vision_out = self.vision_agent.analyze(evidence)
        agent_outputs["vision_agent"] = vision_out
        pipeline_log.append({"agent":"VISION_AGENT","action":f"Detected {len(vision_out['detections'])} object(s)","status":"done"})

        # Stage 3: Forensic
        pipeline_log.append({"agent":"FORENSIC_AGENT","action":"Forensic interpretation via LLM","status":"running"})
        forensic_out = self.forensic_agent.analyze(evidence, fir_out.get("entities",{}))
        agent_outputs["forensic_agent"] = forensic_out
        pipeline_log.append({"agent":"FORENSIC_AGENT","action":f"Violence: {forensic_out['violence_level']} ({forensic_out['violence_score']})","status":"done"})

        # Stage 4: Knowledge Graph
        tokens = []
        for ev in evidence:
            for w in f"{ev.get('description','')} {ev.get('text','')}".split():
                c = w.strip(".,!?()").lower()
                if len(c) > 2: tokens.append(c)
        for vals in fir_out.get("entities",{}).values():
            tokens.extend(v.lower() for v in vals)
        pipeline_log.append({"agent":"KNOWLEDGE_GRAPH","action":"Traversing graph","status":"running"})
        kg_out = self.kg_agent.analyze(tokens, location, fir_out.get("time_period","unknown"))
        agent_outputs["knowledge_graph"] = kg_out
        pipeline_log.append({"agent":"KNOWLEDGE_GRAPH","action":f"Scored {len(kg_out['graph_scores'])} type(s)","status":"done"})

        # Stage 5: Inference
        ev_text = " | ".join(f"{e.get('description','')} {e.get('text','')}" for e in evidence)
        pipeline_log.append({"agent":"INFERENCE_ENGINE","action":"LLM synthesis of all agent outputs","status":"running"})
        inference_out = self.inference_agent.synthesize(
            fir_text, location, time_str, ev_text,
            fir_out, vision_out, forensic_out, kg_out)
        agent_outputs["inference_engine"] = inference_out
        pipeline_log.append({"agent":"INFERENCE_ENGINE","action":f"Generated {len(inference_out['scenarios'])} scenario(s)","status":"done"})

        pipeline_log.append({"agent":self.NAME,"action":"Pipeline complete","status":"complete"})

        all_logs = []
        for key in ("fir_analyzer","vision_agent","forensic_agent","knowledge_graph","inference_engine"):
            for line in agent_outputs[key].get("log",[]):
                all_logs.append({"agent":agent_outputs[key]["agent"],"message":line})

        return {
            "scenarios": inference_out["scenarios"],
            "pipeline": pipeline_log,
            "agent_details": {
                "fir_analyzer": {"crime_indicators":fir_out["crime_indicators"],"entities":fir_out.get("entities",{}),"time_period":fir_out.get("time_period","")},
                "vision_agent": {"detections":vision_out["detections"]},
                "forensic_agent": {"interpretations":forensic_out["interpretations"],"violence_score":forensic_out["violence_score"],"violence_level":forensic_out["violence_level"]},
                "knowledge_graph": {"graph_scores":kg_out["graph_scores"],"total_nodes":len(_kg.nodes),"total_edges":len(_kg.edges)},
            },
            "reasoning_trace": all_logs,
        }


def run_evidence_analysis(fir_text, location, time_str, evidence):
    orchestrator = OrchestratorAgent()
    return orchestrator.run_pipeline(fir_text, location, time_str, evidence)
