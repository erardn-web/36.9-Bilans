"""
tests/leg_press.py — 1RM Leg Press (séparé du testing musculaire)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


def _compute_1rm(weight_kg, reps):
    if not weight_kg or not reps or reps<=0 or weight_kg<=0: return None
    if reps==1:  return round(weight_kg, 1)
    if reps>10:  return round(weight_kg*(1+reps/30), 1)
    return round(weight_kg/(1.0278-0.0278*reps), 1)


def _interpret(w, bw=None):
    if w is None: return {"color":"#888","interpretation":""}
    if bw and bw>0:
        ratio = w/bw
        if ratio>=2.0: return {"color":"#388e3c","interpretation":f"Très bon ({ratio:.1f}× PC)"}
        if ratio>=1.5: return {"color":"#8bc34a","interpretation":f"Bon ({ratio:.1f}× PC)"}
        if ratio>=1.0: return {"color":"#f57c00","interpretation":f"Moyen ({ratio:.1f}× PC)"}
        return {"color":"#d32f2f","interpretation":f"Faible ({ratio:.1f}× PC)"}
    if w>=150: return {"color":"#388e3c","interpretation":"≥ 150 kg"}
    if w>=100: return {"color":"#f57c00","interpretation":"100–149 kg"}
    return {"color":"#d32f2f","interpretation":"< 100 kg"}


def _lf(lv, key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=float(v); return r if r!=0.0 else None
    except: return None


def _li(lv, key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=int(float(v)); return r if r!=0 else None
    except: return None


@register_test
class LegPress(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"leg_press","nom":"Leg Press — 1RM Brzycki/Epley","tab_label":"🏋️ Leg Press 1RM",
                "categorie":"test_clinique","tags":["force", "membres inférieurs", "presse", "1RM", "musculaire"],"description":"Estimation 1RM par formule Brzycki/Epley"}

    @classmethod
    def fields(cls):
        return ["lp_charge_kg","lp_reps","lp_1rm_estime","lp_interpretation","lp_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">1RM Leg Press (estimé)</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Entrez la charge et le nombre de répétitions réalisées. '
            'Le 1RM est estimé via Brzycki (1–10 rép.) ou Epley (&gt; 10 rép.).</div>',
            unsafe_allow_html=True)

        lp1, lp2 = st.columns(2)
        with lp1:
            lp_charge = st.number_input("Charge utilisée (kg)", 0.0, 500.0,
                value=_lf(lv,"lp_charge_kg"), step=2.5,
                key=f"{key_prefix}_lp_charge", help="0 = non réalisé")
        with lp2:
            lp_reps = st.number_input("Répétitions réalisées", 0, 30,
                value=_li(lv,"lp_reps"), step=1,
                key=f"{key_prefix}_lp_reps", help="0 = non réalisé")

        lp_1rm=None; lp_interp=""
        if lp_charge and lp_charge>0 and lp_reps and lp_reps>0:
            lp_1rm   = _compute_1rm(lp_charge, int(lp_reps))
            r_interp = _interpret(lp_1rm)
            lp_interp = r_interp["interpretation"]
            st.markdown(
                f'<div class="score-box" style="background:{r_interp["color"]};">'
                f'1RM estimé : <b>{lp_1rm} kg</b> — {lp_interp}</div>',
                unsafe_allow_html=True)

        notes = st.text_area("Notes Leg Press", value=lv("lp_notes",""),
                             height=50, key=f"{key_prefix}_lp_notes")
        return {"lp_charge_kg":lp_charge or "","lp_reps":lp_reps or "",
                "lp_1rm_estime":lp_1rm or "","lp_interpretation":lp_interp,
                "lp_notes":notes}

    @classmethod
    def score(cls, data):
        try:    w = float(data.get("lp_1rm_estime",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        if w<=0: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        i = _interpret(w)
        return {"score":w,"interpretation":i["interpretation"],"color":i["color"],"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        v = bilan_data.get("lp_1rm_estime","")
        try: return float(v) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("lp_1rm_estime",""))
                vals.append(None if math.isnan(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v and v>0]
        yp = [v for v in vals if v is not None and v==v and v>0]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Bar(x=xp,y=yp,marker_color="#2B57A7",
                text=[f"{v:.0f} kg" for v in yp],textposition="outside"))
        fig.update_layout(height=300,yaxis_title="kg",
                          plot_bgcolor="white",paper_bgcolor="white")
        if xp: st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Charge (kg)":row.get("lp_charge_kg","—"),
                 "Reps":row.get("lp_reps","—"),"1RM estimé":row.get("lp_1rm_estime","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
