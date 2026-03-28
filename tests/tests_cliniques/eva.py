"""tests/tests_cliniques/eva.py — EVA/NRS Douleur Lombalgie (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

LOCALISATIONS = [
    "Lombaire basse (L4-S1)","Lombaire haute (T12-L3)",
    "Sacro-iliaque droite","Sacro-iliaque gauche",
    "Fessière droite","Fessière gauche",
    "Irradiation membre inf. droit","Irradiation membre inf. gauche","Bilatérale",
]
TYPES_DOULEUR = [
    "Mécanique (liée au mouvement)","Inflammatoire (nocturne, raideur matinale)",
    "Neuropathique (brûlure, décharge électrique)","Mixte",
]
FACTEURS_AGG = [
    "Flexion","Extension","Rotation droite","Rotation gauche",
    "Latéroflexion droite","Latéroflexion gauche",
    "Station assise prolongée","Station debout prolongée",
    "Marche","Montée/descente d'escaliers","Port de charges","Toux / éternuement",
]
FACTEURS_SOUL = [
    "Repos","Chaleur","Froid","Mouvement doux",
    "Position couchée sur le dos","Position couchée sur le ventre",
    "Position fœtale","Marche","Antalgiques","AINS","Étirements",
]

@register_test
class EVA(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"eva","nom":"EVA / Douleur","tab_label":"📊 EVA / Douleur",
                "categorie":"test_clinique","tags":["douleur", "EVA", "EN", "toutes pathologies"],"description":"EVA repos/mouvement/nuit + caractéristiques douleur"}

    @classmethod
    def fields(cls):
        return ["s_eva_repos","s_eva_mouvement","s_eva_nuit",
                "s_douleur_localisation","s_type_douleur",
                "s_facteurs_aggravants","s_facteurs_soulageants",
                "s_debut_douleur","s_duree_episode","s_antecedents",
                "s_arret_travail","s_reveil_nuit"]

    def render(self, lv, key_prefix):
        def _eva_default(key):
            v=lv(key,None)
            if v is None or str(v).strip() in ("","None"): return "—"
            try: return int(float(v))
            except: return "—"

        EVA_OPTS=["—",0,1,2,3,4,5,6,7,8,9,10]
        st.markdown('<div class="section-title">Intensité de la douleur (EVA)</div>',
                    unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            eva_r=st.select_slider("EVA repos (0–10)",options=EVA_OPTS,
                value=_eva_default("s_eva_repos"),key=f"{key_prefix}_eva_r",
                format_func=lambda x:"Non renseigné" if x=="—" else str(x))
            eva_m=st.select_slider("EVA mouvement (0–10)",options=EVA_OPTS,
                value=_eva_default("s_eva_mouvement"),key=f"{key_prefix}_eva_m",
                format_func=lambda x:"Non renseigné" if x=="—" else str(x))
            eva_n=st.select_slider("EVA nuit (0–10)",options=EVA_OPTS,
                value=_eva_default("s_eva_nuit"),key=f"{key_prefix}_eva_n",
                format_func=lambda x:"Non renseigné" if x=="—" else str(x))
            def ec(s): return "#388e3c" if s<=3 else "#f57c00" if s<=6 else "#d32f2f"
            for lbl,val in [("Repos",eva_r),("Mouvement",eva_m),("Nuit",eva_n)]:
                if val!="—":
                    st.markdown(f'<small style="color:{ec(val)}">● EVA {lbl} : <b>{val}/10</b></small>',
                                unsafe_allow_html=True)
        with c2:
            loc_stored=[x for x in str(lv("s_douleur_localisation","")).split("|") if x in LOCALISATIONS]
            localisation=st.multiselect("Localisation",LOCALISATIONS,
                default=loc_stored,key=f"{key_prefix}_loc")
            td_opts=["— Non renseigné —"]+TYPES_DOULEUR
            td_stored=lv("s_type_douleur","")
            td_idx=td_opts.index(td_stored) if td_stored in td_opts else 0
            type_douleur=st.selectbox("Type de douleur",td_opts,index=td_idx,
                key=f"{key_prefix}_type")

        st.markdown('<div class="section-title">Facteurs</div>', unsafe_allow_html=True)
        fa1,fa2=st.columns(2)
        with fa1:
            agg_stored=[x for x in str(lv("s_facteurs_aggravants","")).split("|") if x in FACTEURS_AGG]
            aggravants=st.multiselect("Facteurs aggravants",FACTEURS_AGG,
                default=agg_stored,key=f"{key_prefix}_agg")
        with fa2:
            soul_stored=[x for x in str(lv("s_facteurs_soulageants","")).split("|") if x in FACTEURS_SOUL]
            soulageants=st.multiselect("Facteurs soulageants",FACTEURS_SOUL,
                default=soul_stored,key=f"{key_prefix}_soul")

        st.markdown('<div class="section-title">Historique</div>', unsafe_allow_html=True)
        h1,h2=st.columns(2)
        with h1:
            debut=st.text_input("Début de la douleur",value=lv("s_debut_douleur",""),
                key=f"{key_prefix}_debut")
            duree=st.text_input("Durée épisode actuel",value=lv("s_duree_episode",""),
                key=f"{key_prefix}_duree")
        with h2:
            atcd=st.text_area("Antécédents",value=lv("s_antecedents",""),height=80,
                key=f"{key_prefix}_atcd")
        ck1,ck2=st.columns(2)
        with ck1:
            arret=st.checkbox("Arrêt de travail",value=lv("s_arret_travail","")=="Oui",
                key=f"{key_prefix}_arret")
        with ck2:
            reveil=st.checkbox("Se réveille la nuit",value=lv("s_reveil_nuit","")=="Oui",
                key=f"{key_prefix}_reveil")

        return {
            "s_eva_repos":"" if eva_r=="—" else eva_r,
            "s_eva_mouvement":"" if eva_m=="—" else eva_m,
            "s_eva_nuit":"" if eva_n=="—" else eva_n,
            "s_douleur_localisation":"|".join(localisation),
            "s_type_douleur":"" if type_douleur=="— Non renseigné —" else type_douleur,
            "s_facteurs_aggravants":"|".join(aggravants),
            "s_facteurs_soulageants":"|".join(soulageants),
            "s_debut_douleur":debut,"s_duree_episode":duree,"s_antecedents":atcd,
            "s_arret_travail":"Oui" if arret else "Non",
            "s_reveil_nuit":"Oui" if reveil else "Non",
        }

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("s_eva_repos","s_eva_mouvement","s_eva_nuit"):
            v=str(bilan_data.get(k,"")).strip()
            if v not in ("","None","nan","—"): return True
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig=go.Figure()
        for key,label,color in [("s_eva_repos","Repos","#2B57A7"),
                                  ("s_eva_mouvement","Mouvement","#C4603A"),
                                  ("s_eva_nuit","Nuit","#7B1FA2")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                v=str(row.get(key,"")).strip()
                try: vals.append(int(float(v)) if v not in ("","None","nan","—") else None)
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]
            yp=[v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v}/10" for v in yp],textposition="top center"))
        for y,color,label in [(4,"#388e3c","4 léger"),(7,"#f57c00","7 sévère")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,11],title="EVA /10"),height=320,
                          legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"Repos":row.get("s_eva_repos","—"),
               "Mouvement":row.get("s_eva_mouvement","—"),"Nuit":row.get("s_eva_nuit","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
