"""tests/tests_cliniques/testing_epaule.py — Testing musculaire épaule (MRC 0-5)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

MUSCLES_EPAULE = [
    ("ep_m_sus_ep",   "Sus-épineux",      "Abduction 0–30°, bras horizontal légèrement en avant (Full can)"),
    ("ep_m_sous_ep",  "Sous-épineux",     "Rotation externe contre résistance, coude à 90°"),
    ("ep_m_sub",      "Subscapulaire",    "Rotation interne contre résistance (Belly press / lift-off)"),
    ("ep_m_pt_rond",  "Petit rond",       "Rotation externe bras en abduction"),
    ("ep_m_delt_ant", "Deltoïde antérieur","Flexion contre résistance"),
    ("ep_m_delt_moy", "Deltoïde moyen",   "Abduction contre résistance"),
    ("ep_m_delt_post","Deltoïde postérieur","Extension horizontale contre résistance"),
    ("ep_m_trap_sup", "Trapèze supérieur","Haussement d'épaule contre résistance"),
    ("ep_m_trap_moy", "Trapèze moyen",    "Rétraction scapulaire contre résistance"),
    ("ep_m_grand_den","Grand dentelé",    "Flexion 90°, push-up contre mur (winging scapulaire)"),
]
MRC_OPTS  = [None,0,1,2,3,4,5]
MRC_FMT   = {None:"—",0:"0",1:"1",2:"2",3:"3",4:"4",5:"5"}

def _mrc_color(v):
    if v is None: return "#888"
    return ["#d32f2f","#e64a19","#f57c00","#f9a825","#8bc34a","#388e3c"][min(v,5)]

@register_test
class TestingEpaule(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"testing_epaule","nom":"Testing épaule","tab_label":"💪 Testing épaule",
                "categorie":"test_clinique","tags":["épaule", "membre supérieur", "force", "testing", "MRC"],
                "description":"Testing musculaire épaule MRC 0–5 (coiffe + deltoïde + scapulaire)"}

    @classmethod
    def fields(cls):
        return [f"{m[0]}_{s}" for m in MUSCLES_EPAULE for s in ("d","g")] + ["ep_musc_notes"]

    def render(self, lv, key_prefix):
        def _li(k):
            v=lv(k,None)
            if v is None or str(v).strip() in ("","None"): return None
            try: return int(float(v))
            except: return None

        st.markdown('<div class="section-title">Testing musculaire — Épaule (MRC 0–5)</div>',
                    unsafe_allow_html=True)
        h0,hd,hg=st.columns([3,1,1])
        h0.markdown("**Muscle**"); hd.markdown("**Droit**"); hg.markdown("**Gauche**")
        st.markdown("---")

        collected={}
        for key,label,desc in MUSCLES_EPAULE:
            c0,cd,cg=st.columns([3,1,1])
            c0.markdown(f"**{label}**")
            c0.markdown(f"<small style='color:#888'>{desc}</small>",unsafe_allow_html=True)
            for side,col in [("d",cd),("g",cg)]:
                k=f"{key}_{side}"
                with col:
                    chosen=st.select_slider("",options=MRC_OPTS,value=_li(k),
                        format_func=lambda x:MRC_FMT.get(x,str(x)),
                        key=f"{key_prefix}_{k}",label_visibility="collapsed")
                if chosen is not None:
                    st.markdown(f'<span style="color:{_mrc_color(chosen)};font-weight:600">'
                                f'{chosen}/5</span>',unsafe_allow_html=True)
                collected[k]="" if chosen is None else chosen

        notes=st.text_area("Notes",value=lv("ep_musc_notes",""),height=60,
                           key=f"{key_prefix}_ep_musc_notes")
        collected["ep_musc_notes"]=notes
        return collected

    @classmethod
    def is_filled(cls,bilan_data):
        return any(str(bilan_data.get(f"{m[0]}_d","")).strip() not in ("","None","nan")
                   for m in MUSCLES_EPAULE)

    @classmethod
    def render_evolution(cls,bilans_df,labels):
        import pandas as pd
        muscles=["Sus-épineux","Sous-épineux","Subscapulaire","Deltoïde moy."]
        keys=["ep_m_sus_ep","ep_m_sous_ep","ep_m_sub","ep_m_delt_moy"]
        rows=[]
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            r={"Bilan":lbl}
            for k,m in zip(keys,muscles):
                r[f"{m} D"]=row.get(f"{k}_d","—")
                r[f"{m} G"]=row.get(f"{k}_g","—")
            rows.append(r)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
