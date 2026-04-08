"""tests/questionnaires/constant_murley.py — Score de Constant-Murley (épaule)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


@register_test
class ConstantMurley(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"constant_murley","nom":"Constant-Murley — Épaule","tab_label":"📐 Constant","categorie":"questionnaire",
                "tags":["épaule","fonctionnel","force","amplitude"],
                "description":"Score de Constant-Murley — 4 sections : douleur, AVQ, amplitude, force /100"}

    @classmethod
    def fields(cls):
        return ["cm_douleur","cm_avq_activite","cm_avq_travail","cm_avq_loisirs","cm_avq_sommeil",
                "cm_amp_flex","cm_amp_abd","cm_amp_re","cm_amp_ri",
                "cm_force_kg","cm_score_total","cm_score_ajuste"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score Constant-Murley (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📐 Score de Constant-Murley</div>', unsafe_allow_html=True)
        collected = {}

        # Douleur /15
        st.markdown("**Douleur (0=sévère, 15=aucune)**")
        raw=lv("cm_douleur",None)
        try: d=int(float(raw)) if raw not in (None,"","None") else 0
        except: d=0
        douleur=st.slider("Niveau de douleur",0,15,d,key=f"{key_prefix}_cm_d")
        collected["cm_douleur"]=douleur

        # AVQ /20
        st.markdown("**Activités de la vie quotidienne /20**")
        c1,c2=st.columns(2)
        raw=lv("cm_avq_activite",None)
        try: act=int(float(raw)) if raw not in (None,"","None") else 0
        except: act=0
        activite=c1.selectbox("Niveau d'activité",list(range(5)),index=act,
            format_func=lambda x:["0 — Incapable","1 — Niveau très réduit","2 — Niveau réduit","3 — Légère limitation","4 — Activité normale"][x],
            key=f"{key_prefix}_cm_act")
        raw=lv("cm_avq_travail",None)
        try: trav=int(float(raw)) if raw not in (None,"","None") else 0
        except: trav=0
        travail=c1.selectbox("Travail",list(range(5)),index=trav,
            format_func=lambda x:["0 — Incapable","1 — Travail très léger","2 — Travail léger","3 — Travail modéré","4 — Travail complet"][x],
            key=f"{key_prefix}_cm_trav")
        raw=lv("cm_avq_loisirs",None)
        try: lois=int(float(raw)) if raw not in (None,"","None") else 0
        except: lois=0
        loisirs=c2.selectbox("Loisirs/sport",list(range(5)),index=lois,
            format_func=lambda x:["0 — Incapable","1 — Loisirs très légers","2 — Loisirs légers","3 — Loisirs modérés","4 — Tous loisirs"][x],
            key=f"{key_prefix}_cm_lois")
        raw=lv("cm_avq_sommeil",None)
        try: somm=int(float(raw)) if raw not in (None,"","None") else 0
        except: somm=0
        sommeil=c2.selectbox("Sommeil",list(range(3)),index=min(somm,2),
            format_func=lambda x:["0 — Perturbé par la douleur","1 — Légèrement perturbé","2 — Pas perturbé"][x],
            key=f"{key_prefix}_cm_somm")
        avq=min(activite+travail+loisirs+sommeil,20)
        collected.update({"cm_avq_activite":activite,"cm_avq_travail":travail,"cm_avq_loisirs":loisirs,"cm_avq_sommeil":sommeil})

        # Amplitudes /40
        st.markdown("**Amplitudes articulaires /40**")
        c3,c4=st.columns(2)
        def _amp(key,label,maxi,col):
            raw=lv(key,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            return col.number_input(label,0,maxi,v,key=f"{key_prefix}_{key}")
        flex=_amp("cm_amp_flex","Flexion (°)",180,c3)
        abd=_amp("cm_amp_abd","Abduction (°)",180,c3)
        re=_amp("cm_amp_re","Rotation externe (°)",40,c4)
        ri_opts=["0 — Pas derrière le dos","2 — Face dos/fesse","4 — Taille","6 — Vertèbre L3","8 — Vertèbre T12","10 — Omoplate"]
        raw=lv("cm_amp_ri",None)
        try: ri_idx=int(float(raw))//2 if raw not in (None,"","None") else 0
        except: ri_idx=0
        ri_sel=c4.selectbox("Rotation interne",range(6),index=min(ri_idx,5),format_func=lambda x:ri_opts[x],key=f"{key_prefix}_cm_ri")
        ri=ri_sel*2
        flex_s=10 if flex>=150 else 8 if flex>=120 else 6 if flex>=90 else 4 if flex>=60 else 2 if flex>=30 else 0
        abd_s=10 if abd>=150 else 8 if abd>=120 else 6 if abd>=90 else 4 if abd>=60 else 2 if abd>=30 else 0
        re_s=10 if re>=40 else 6 if re>=30 else 4 if re>=20 else 2 if re>=10 else 0
        amp_total=min(flex_s+abd_s+re_s+ri,40)
        collected.update({"cm_amp_flex":flex,"cm_amp_abd":abd,"cm_amp_re":re,"cm_amp_ri":ri})

        # Force /25
        st.markdown("**Force musculaire**")
        raw=lv("cm_force_kg",None)
        try: fkg=float(raw) if raw not in (None,"","None") else 0.0
        except: fkg=0.0
        force_kg=st.number_input("Force en abduction (kg)",0.0,25.0,fkg,0.5,key=f"{key_prefix}_cm_force")
        force_s=min(int(force_kg*2),25)
        collected["cm_force_kg"]=force_kg

        total=douleur+avq+amp_total+force_s
        collected["cm_score_total"]=total
        collected["cm_score_ajuste"]=total  # ajustement âge/sexe possible
        color="#388e3c" if total>=80 else "#f57c00" if total>=55 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Constant-Murley : {total}/100 | Douleur:{douleur} AVQ:{avq} Amp:{amp_total} Force:{force_s}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("cm_score_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=80 else "#f57c00" if s>=55 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("cm_score_total",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("cm_score_total","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Constant",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Constant":r.get("cm_score_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
