"""tests/tests_cliniques/spirometrie.py — Spirométrie BPCO (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

@register_test
class Spirometrie(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"spirometrie","nom":"Spirométrie","tab_label":"💨 Spirométrie",
                "categorie":"test_clinique","tags":["BPCO", "respiratoire", "poumon", "VEMS", "CVF"],"description":"VEMS, CVF, ratio, stade GOLD"}

    @classmethod
    def fields(cls):
        return ["spiro_vems","spiro_cvf","spiro_ratio","spiro_vems_pct","spiro_cvf_pct",
                "spiro_gold","spiro_notes","spo2_repos"]

    def render(self, lv, key_prefix):
        def _lf(k):
            v=lv(k,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None

        st.markdown('<div class="section-title">Spirométrie</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Valeurs post-bronchodilatateur si disponibles.</div>',
                    unsafe_allow_html=True)
        s1,s2 = st.columns(2)
        with s1:
            vems  = st.number_input("VEMS (L)",0.0,8.0,_lf("spiro_vems"),0.01,
                                    key=f"{key_prefix}_vems",help="Volume Expiratoire Maximal Seconde")
            cvf   = st.number_input("CVF (L)",0.0,10.0,_lf("spiro_cvf"),0.01,
                                    key=f"{key_prefix}_cvf",help="Capacité Vitale Forcée")
            ratio = st.number_input("VEMS/CVF (%)",0.0,100.0,_lf("spiro_ratio"),0.1,
                                    key=f"{key_prefix}_ratio")
        with s2:
            vems_pct = st.number_input("VEMS % prédit",0.0,200.0,_lf("spiro_vems_pct"),0.1,
                                       key=f"{key_prefix}_vems_pct")
            cvf_pct  = st.number_input("CVF % prédit",0.0,200.0,_lf("spiro_cvf_pct"),0.1,
                                       key=f"{key_prefix}_cvf_pct")
            gold_opts = ["— Non renseigné —","GOLD 1 (léger ≥ 80%)","GOLD 2 (modéré 50–79%)",
                         "GOLD 3 (sévère 30–49%)","GOLD 4 (très sévère < 30%)"]
            stored_gold = lv("spiro_gold","— Non renseigné —")
            gold = st.selectbox("Stade GOLD", gold_opts,
                index=gold_opts.index(stored_gold) if stored_gold in gold_opts else 0,
                key=f"{key_prefix}_gold")

        if vems_pct and vems_pct > 0:
            if vems_pct>=80:   gc,gi = "#388e3c","GOLD 1 — Léger"
            elif vems_pct>=50: gc,gi = "#f57c00","GOLD 2 — Modéré"
            elif vems_pct>=30: gc,gi = "#e64a19","GOLD 3 — Sévère"
            else:              gc,gi = "#d32f2f","GOLD 4 — Très sévère"
            st.markdown(f'<div class="score-box" style="background:{gc};">'
                        f'VEMS {vems_pct}% prédit → {gi}</div>', unsafe_allow_html=True)

        spo2_r = st.number_input("SpO₂ repos (%)",0.0,100.0,_lf("spo2_repos"),0.1,
                                  key=f"{key_prefix}_spo2r",help="0 = non mesuré")
        spiro_notes = st.text_area("Notes",value=lv("spiro_notes",""),height=60,
                                   key=f"{key_prefix}_notes")
        return {"spiro_vems":vems or "","spiro_cvf":cvf or "","spiro_ratio":ratio or "",
                "spiro_vems_pct":vems_pct or "","spiro_cvf_pct":cvf_pct or "",
                "spiro_gold":"" if gold=="— Non renseigné —" else gold,
                "spo2_repos":spo2_r or "","spiro_notes":spiro_notes}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("spiro_vems_pct","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("spiro_vems_pct",""))
                vals.append(None if not math.isfinite(f) or f<=0 else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="VEMS % prédit",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        for y,color,label in [(80,"#388e3c","GOLD 1"),(50,"#f57c00","GOLD 2"),(30,"#d32f2f","GOLD 3")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis_title="VEMS % prédit",height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"VEMS (L)":row.get("spiro_vems","—"),"CVF (L)":row.get("spiro_cvf","—"),
               "VEMS %":row.get("spiro_vems_pct","—"),"GOLD":row.get("spiro_gold","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
