"""
tests/tests_cliniques/testing_mi.py — Testing musculaire MI (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

MUSCLE_GROUPS = [
    ("hip_flex",  "Fléchisseurs de hanche",      "Décubitus dorsal — flexion contre résistance"),
    ("hip_ext",   "Extenseurs de hanche",         "Décubitus ventral — extension contre résistance"),
    ("hip_abd",   "Abducteurs de hanche",         "Décubitus latéral — abduction contre résistance"),
    ("hip_add",   "Adducteurs de hanche",         "Décubitus latéral — adduction contre résistance"),
    ("knee_ext",  "Extenseurs genou (Quadriceps)","Assis — extension contre résistance"),
    ("knee_flex", "Fléchisseurs genou (IJ)",      "Décubitus ventral — flexion contre résistance"),
    ("ankle_df",  "Dorsiflexeurs cheville",       "Décubitus dorsal — dorsiflexion contre résistance"),
    ("ankle_pf",  "Plantarflexeurs cheville",     "Debout — montée sur pointe des pieds"),
]
MRC_SCALE  = [(0,"0"),(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5")]
MRC_VALUES = [0,1,2,3,4,5]
SIDES      = ["d","g"]


def _get_muscle_key(key_sfx, side):
    return f"musc_{key_sfx}_{side}"


def _compute_1rm(weight_kg, reps):
    if not weight_kg or not reps or reps<=0 or weight_kg<=0: return None
    if reps==1:    return round(weight_kg, 1)
    if reps>10:    return round(weight_kg*(1+reps/30), 1)
    return round(weight_kg/(1.0278-0.0278*reps), 1)


def _interpret_leg_press(w, bw=None):
    if w is None: return {"color":"#888","interpretation":""}
    if bw and bw>0:
        ratio = w/bw
        if ratio>=2.0:   return {"color":"#388e3c","interpretation":f"Très bon ({ratio:.1f}× PC)"}
        if ratio>=1.5:   return {"color":"#8bc34a","interpretation":f"Bon ({ratio:.1f}× PC)"}
        if ratio>=1.0:   return {"color":"#f57c00","interpretation":f"Moyen ({ratio:.1f}× PC)"}
        return {"color":"#d32f2f","interpretation":f"Faible ({ratio:.1f}× PC)"}
    if w>=150: return {"color":"#388e3c","interpretation":"≥ 150 kg"}
    if w>=100: return {"color":"#f57c00","interpretation":"100–149 kg"}
    return {"color":"#d32f2f","interpretation":"< 100 kg"}


def _load_float(lv, key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=float(v); return r if r!=0.0 else None
    except: return None


def _load_int(lv, key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=int(float(v)); return r if r!=0 else None
    except: return None


@register_test
class TestingMI(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"testing_mi","nom":"Testing musculaire MI",
                "tab_label":"💪 Testing MI","categorie":"test_clinique",
                "description":"Testing MRC membres inférieurs (0–5)"}

    @classmethod
    def fields(cls):
        fields = []
        for key_sfx,_,_ in MUSCLE_GROUPS:
            for side in SIDES:
                fields.append(_get_muscle_key(key_sfx, side))
        fields += ["musc_notes"]
        return fields

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Testing musculaire — Membres inférieurs</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Testing manuel selon l\'échelle MRC (0–5). '
            'D = côté droit · G = côté gauche</div>',
            unsafe_allow_html=True)

        # En-tête
        hcol, hd, hg = st.columns([3,1,1])
        with hcol: st.markdown("**Groupe musculaire**")
        with hd:   st.markdown("**Droit (0–5)**")
        with hg:   st.markdown("**Gauche (0–5)**")
        st.markdown("---")

        collected     = {}
        muscle_answers = {}

        for key_sfx, label, desc in MUSCLE_GROUPS:
            col_lbl, col_d, col_g = st.columns([3,1,1])
            with col_lbl:
                st.markdown(f"**{label}**")
                st.markdown(f"<small style='color:#888'>{desc}</small>", unsafe_allow_html=True)
            for side, col in [("d",col_d),("g",col_g)]:
                k      = _get_muscle_key(key_sfx, side)
                stored = lv(k, "")
                stored_str = str(stored).strip()
                opts   = [None] + MRC_VALUES
                fmt    = {None:"—",0:"0",1:"1",2:"2",3:"3",4:"4",5:"5"}
                default = None if stored_str in ("","None") else int(float(stored_str))
                with col:
                    chosen = st.select_slider(
                        label=f"{key_sfx}_{side}", options=opts, value=default,
                        format_func=lambda x: fmt.get(x, str(x)),
                        key=f"{key_prefix}_musc_{key_sfx}_{side}",
                        label_visibility="collapsed")
                if chosen is not None:
                    muscle_answers[k] = chosen
                    collected[k] = chosen
                else:
                    collected[k] = ""

        # Score global
        vals = [v for v in muscle_answers.values() if v is not None and v==v]
        if vals:
            mean_v = round(sum(vals)/len(vals), 1)
            total  = sum(vals)
            maxi   = len(vals)*5
            color  = "#388e3c" if mean_v>=4 else "#f57c00" if mean_v>=3 else "#d32f2f"
            st.markdown("---")
            st.markdown(
                f'<div class="score-box" style="background:{color};">'
                f'Moyenne MRC : {mean_v}/5 '
                f'<small>({len(vals)} groupes évalués · total {total}/{maxi})</small>'
                f'</div>', unsafe_allow_html=True)

        notes = st.text_area("Notes / observations", value=lv("musc_notes",""),
                             height=70, key=f"{key_prefix}_musc_notes")
        collected["musc_notes"] = notes
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        for key_sfx,_,_ in MUSCLE_GROUPS:
            for side in SIDES:
                v = bilan_data.get(_get_muscle_key(key_sfx,side),"")
                if str(v).strip() not in ("","None","nan"): return True
        return bool(bilan_data.get("lp_1rm_estime",""))

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals_1rm = []
        for _,row in bilans_df.iterrows():
            try:    vals_1rm.append(float(row.get("lp_1rm_estime","")))
            except: vals_1rm.append(None)
        fig = go.Figure()
        xp = [labels[i] for i,v in enumerate(vals_1rm) if v is not None and v==v and v>0]
        yp = [v for v in vals_1rm if v is not None and v==v and v>0]
        if xp:
            fig.add_trace(go.Bar(x=xp,y=yp,name="1RM (kg)",marker_color="#2B57A7",
                text=[f"{v:.0f} kg" for v in yp],textposition="outside"))
        fig.update_layout(height=300,yaxis_title="kg",title="1RM Leg Press",
                          plot_bgcolor="white",paper_bgcolor="white")
        if xp: st.plotly_chart(fig,use_container_width=True)

        rows = []
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            r = {"Bilan":lbl}
            for key_sfx,label_m,_ in MUSCLE_GROUPS:
                vd = row.get(_get_muscle_key(key_sfx,"d"),"—")
                vg = row.get(_get_muscle_key(key_sfx,"g"),"—")
                r[f"{label_m[:12]} D"] = vd
                r[f"{label_m[:12]} G"] = vg
            r["1RM (kg)"] = row.get("lp_1rm_estime","—")
            rows.append(r)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
