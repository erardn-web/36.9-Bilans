"""tests/tests_cliniques/tug.py — TUG Timed Up and Go (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

@register_test
class TUG(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tug","nom":"TUG — Timed Up and Go","tab_label":"⏱️ TUG",
                "categorie":"test_clinique","description":"Lever, marcher 3m, retour — normal < 12 sec"}

    @classmethod
    def fields(cls):
        return ["tug_temps","tug_aide","tug_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">TUG — Timed Up and Go</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Lever, marcher 3 m, demi-tour, revenir, s\'asseoir. '
                    'Normal &lt; 12 sec chez l\'adulte âgé. &lt; 20 sec = indépendant.</div>',
                    unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            stored = lv("tug_temps",None)
            try:    default = float(stored) if stored not in (None,"","None") else None
            except: default = None
            tug_temps = st.number_input("Temps (secondes)", 0.0, 120.0,
                                        default, 0.1, key=f"{key_prefix}_tug_t",
                                        help="0 = non mesuré")
        with t2:
            aide_opts = ["— Non renseigné —","Aucune","Canne","Déambulateur","Autre"]
            stored_aide = lv("tug_aide","")
            aide_idx = aide_opts.index(stored_aide) if stored_aide in aide_opts else 0
            tug_aide = st.selectbox("Aide technique", aide_opts,
                                    index=aide_idx, key=f"{key_prefix}_tug_aide")

        tug_interp = ""
        if tug_temps and tug_temps > 0:
            if tug_temps < 10:   tc,tug_interp = "#388e3c","Mobilité normale (< 10 sec)"
            elif tug_temps < 12: tc,tug_interp = "#8bc34a","Bon score (10–11 sec)"
            elif tug_temps < 20: tc,tug_interp = "#f57c00","Risque modéré (12–19 sec)"
            else:                tc,tug_interp = "#d32f2f","Risque élevé de chute (≥ 20 sec)"
            st.markdown(f'<div class="score-box" style="background:{tc};">'
                        f'TUG : {tug_temps} sec — {tug_interp}</div>', unsafe_allow_html=True)
        return {
            "tug_temps":       tug_temps or "",
            "tug_aide":        "" if tug_aide == "— Non renseigné —" else tug_aide,
            "tug_interpretation": tug_interp,
        }

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("tug_temps",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        if s<=0: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#388e3c" if s<10 else "#8bc34a" if s<12 else "#f57c00" if s<20 else "#d32f2f"
        return {"score":s,"interpretation":data.get("tug_interpretation",""),"color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("tug_temps","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("tug_temps",""))
                vals.append(None if not math.isfinite(f) or f<=0 else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="TUG (sec)",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"{v:.1f}s" for v in yp],textposition="top center"))
        for y,color,label in [(12,"#f57c00","12s seuil"),(20,"#d32f2f","20s risque élevé")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(title="Secondes"),height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"TUG (sec)":row.get("tug_temps","—"),"Aide":row.get("tug_aide","—"),
                 "Interprétation":row.get("tug_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
