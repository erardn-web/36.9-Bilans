"""tests/tests_cliniques/luomajoki.py — Tests de Luomajoki (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

LUOM_TESTS=[
    ("luom_waiters_bow","1. Waiters Bow (hip hinge)","Le patient se penche en avant en fléchissant les hanches sans flexion lombaire. Échec si flexion/extension lombaire compensatoire."),
    ("luom_pelvic_tilt","2. Pelvic Tilt (debout)","Antéversion et rétroversion pelviennes. Échec si mouvement lombaire au lieu du mouvement pelvien pur."),
    ("luom_knee_lift","3. Knee Lift (debout)","Lever du genou à 90° en unipodal. Échec si inclinaison lombaire ou rotation du bassin."),
    ("luom_one_leg_stance","4. One-Leg Stance","Maintien sur un pied 10 sec. Échec si oscillation lombaire ou chute du bassin > 2 cm."),
    ("luom_sitting_knee_ext","5. Sitting Knee Extension","Extension du genou assis. Échec si flexion lombaire compensatoire."),
    ("luom_prone_knee_bend","6. Prone Knee Bend","Flexion du genou 90° en décubitus ventral. Échec si antéversion pelvienne ou extension lombaire compensatoire."),
]
LUOM_OPTS=["— Non testé —","✅ Réussi","❌ Échoué"]
LUOM_KEYS=[f"o_{t[0]}" for t in LUOM_TESTS]

@register_test
class Luomajoki(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"luomajoki","nom":"Luomajoki — Contrôle moteur","tab_label":"🔄 Luomajoki — Contrôle moteur",
                "categorie":"test_clinique","tags":["lombalgie", "contrôle moteur", "rachis", "stabilité"],
                "description":"Contrôle moteur lombaire /6, seuil ≥ 3 échecs significatif"}

    @classmethod
    def fields(cls):
        return LUOM_KEYS + ["o_luomajoki_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Tests de Luomajoki — Contrôle moteur lombaire</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box"><small>✅ Réussi = contrôle correct · ❌ Échoué = perte de contrôle. '                    'Score ≥ 3 échecs = cliniquement significatif.</small></div>',
                    unsafe_allow_html=True)
        luom_scores=[]; collected={}
        lc1,lc2=st.columns(2)
        for i,(lkey,lname,ldesc) in enumerate(LUOM_TESTS):
            stored=lv(f"o_{lkey}","")
            idx=LUOM_OPTS.index(stored) if stored in LUOM_OPTS else 0
            with (lc1 if i%2==0 else lc2):
                st.markdown(f"**{lname}**  \n<small style='color:#666'>{ldesc}</small>",
                            unsafe_allow_html=True)
                chosen=st.radio(lname,LUOM_OPTS,index=idx,horizontal=True,
                                key=f"{key_prefix}_{lkey}",label_visibility="collapsed")
                collected[f"o_{lkey}"]="" if chosen=="— Non testé —" else chosen
                if chosen=="❌ Échoué": luom_scores.append(1)

        n_echecs=len(luom_scores)
        if n_echecs>0:
            color="#d32f2f" if n_echecs>=3 else "#f57c00"
            st.markdown(f'<div class="score-box" style="background:{color};">'                        f'{n_echecs}/6 tests échoués'                        f'{"  — Dysfonction de contrôle moteur significative" if n_echecs>=3 else ""}'                        f'</div>', unsafe_allow_html=True)
        collected["o_luomajoki_score"]=n_echecs if n_echecs>0 else ""
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        v=str(bilan_data.get("o_luomajoki_score","")).strip()
        return v not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[float(row.get("o_luomajoki_score",0) or 0) for _,row in bilans_df.iterrows()]
        if any(v>0 for v in vals):
            fig=go.Figure()
            fig.add_trace(go.Bar(x=labels,y=vals,
                marker_color=["#d32f2f" if v>=3 else "#f57c00" if v>=1 else "#388e3c" for v in vals],
                text=[f"{int(v)}/6" if v>0 else "—" for v in vals],textposition="outside"))
            fig.add_hline(y=3,line_dash="dot",line_color="#d32f2f",
                          annotation_text="Seuil 3",annotation_position="right")
            fig.update_layout(yaxis=dict(range=[0,7],title="Échecs /6"),
                              height=300,plot_bgcolor="white",paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)
        LUOM_NOMS=["Waiters Bow","Pelvic Tilt","Knee Lift","One-Leg Stance","Sitting Knee Ext.","Prone Knee Bend"]
        rows=[{"Bilan":lbl,"Score /6":row.get("o_luomajoki_score","—"),
               **{n:row.get(f"o_{LUOM_TESTS[i][0]}","—") for i,n in enumerate(LUOM_NOMS)}}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
