"""
tests/tests_cliniques/snif_pimax_pemax.py — SNIF/PImax/PEmax (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import interpret_mip_mep


def _safe_float(v):
    try: return float(v) if v not in (None,"","None") else None
    except: return None


@register_test
class SNIFPimaxPemax(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"snif_pimax_pemax","nom":"SNIF / PImax / PEmax",
                "tab_label":"💪 SNIF / PImax / PEmax","categorie":"test_clinique","tags":["respiratoire", "SHV", "force", "pression", "inspiration"],
                "description":"Forces musculaires respiratoires — mesurées et % prédit"}

    @classmethod
    def fields(cls):
        return ["snif_val","snif_pred","snif_pct",
                "pimax_val","pimax_pred","pimax_pct",
                "pemax_val","pemax_pred","pemax_pct",
                "snif_pimax_pemax_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 SNIF Test · PImax · PEmax</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">'
            '<strong>SNIF</strong> : Sniff Nasal Inspiratory Pressure. '
            '<strong>PImax</strong> : Pression Inspiratoire Maximale (MIP). '
            '<strong>PEmax</strong> : Pression Expiratoire Maximale (MEP). '
            'Valeur normale : ≥ 80% de la valeur prédite.</div>',
            unsafe_allow_html=True)

        collected = {}

        def muscle_row(label, key_val, key_pred, key_pct):
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                v = st.number_input(f"{label} — Mesuré (cmH₂O)",
                    value=_safe_float(lv(key_val,None)),
                    step=1.0, key=f"{key_prefix}_{key_val}")
            with sc2:
                p = st.number_input(f"{label} — Prédit (cmH₂O)",
                    value=_safe_float(lv(key_pred,None)),
                    step=1.0, key=f"{key_prefix}_{key_pred}")
            with sc3:
                if v and p:
                    pct, interp_txt, color = interpret_mip_mep(v, p)
                    st.metric(f"{label} % prédit", f"{pct:.0f}%" if pct else "—")
                    st.markdown(f'<small style="color:{color}">{interp_txt}</small>',
                                unsafe_allow_html=True)
                    collected[key_pct] = round(pct,1) if pct else ""
                else:
                    collected[key_pct] = ""
            collected[key_val]  = v or ""
            collected[key_pred] = p or ""

        muscle_row("SNIF",  "snif_val",  "snif_pred",  "snif_pct")
        st.markdown("---")
        muscle_row("PImax", "pimax_val", "pimax_pred", "pimax_pct")
        st.markdown("---")
        muscle_row("PEmax", "pemax_val", "pemax_pred", "pemax_pct")

        notes = st.text_area("Notes", value=str(lv("snif_pimax_pemax_notes","") or ""),
                             height=80, key=f"{key_prefix}_snif_notes")
        collected["snif_pimax_pemax_notes"] = notes
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("snif_pct","pimax_pct","pemax_pct"):
            v = bilan_data.get(k,"")
            if str(v).strip() not in ("","0","0.0","None","nan"): return True
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key,label,color in [("snif_pct","SNIF % prédit","#2B57A7"),
                                  ("pimax_pct","PImax % prédit","#C4603A"),
                                  ("pemax_pct","PEmax % prédit","#388e3c")]:
            vals = []
            for _,row in bilans_df.iterrows():
                try:    vals.append(float(row.get(key,"")))
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v and v>0]
            yp = [v for v in vals if v is not None and v==v and v>0]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v if v==v else 0}%" for v in yp if v==v],textposition="top center"))
        fig.add_hline(y=80,line_dash="dot",line_color="#388e3c",
                      annotation_text="80% normal",annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,130],title="% valeur prédite"),
                          height=350,legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,
                 "SNIF (cmH₂O)":row.get("snif_val","—"),"SNIF %":row.get("snif_pct","—"),
                 "PImax (cmH₂O)":row.get("pimax_val","—"),"PImax %":row.get("pimax_pct","—"),
                 "PEmax (cmH₂O)":row.get("pemax_val","—"),"PEmax %":row.get("pemax_pct","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
