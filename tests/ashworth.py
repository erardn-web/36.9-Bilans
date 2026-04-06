"""tests/questionnaires/neurologie.py — Barthel, 10MWT, Ashworth, Fugl-Meyer"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Barthel Index ─────────────────────────────────────────────────────────────
@register_test
class AshworthScale(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"ashworth","nom":"Ashworth modifié — Spasticité","tab_label":"💪 Ashworth",
                "categorie":"test_clinique","tags":["spasticité","neurologie","AVC","Parkinson","tonus"],
                "description":"Modified Ashworth Scale — évaluation spasticité musculaire 0-4"}
    MUSCLES=[
        ("ash_ms_epaule","Épaule"),("ash_ms_coude","Coude"),("ash_ms_poignet","Poignet"),
        ("ash_ms_doigts","Doigts"),("ash_mi_hanche","Hanche"),("ash_mi_genou","Genou"),
        ("ash_mi_cheville","Cheville"),
    ]
    OPTS={0:"0 — Pas d'augmentation du tonus",1:"1 — Légère (résistance brève)",
          1.5:"1+ — Légère (résistance >50% ROM)",2:"2 — Augmentation notable",
          3:"3 — Importante (PROM difficile)",4:"4 — Rigidité complète"}
    @classmethod
    def fields(cls):
        fields=[]
        for k,_ in cls.MUSCLES:
            fields+=[f"{k}_d",f"{k}_g"]
        return fields+["ashworth_notes"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 Ashworth modifié — Spasticité</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = pas de spasticité · 4 = rigidité complète. Évaluation passive.</div>', unsafe_allow_html=True)
        collected={}
        vals=list(self.OPTS.keys())
        st.markdown("| Muscle | Droite | Gauche |")
        st.markdown("|---|---|---|")
        for k,label in self.MUSCLES:
            c1,c2,c3=st.columns([2,2,2])
            c1.markdown(f"**{label}**")
            for col,side,fk in [(c2,"D",f"{k}_d"),(c3,"G",f"{k}_g")]:
                raw=lv(fk,None)
                try: stored=float(raw) if raw not in (None,"","None") else 0
                except: stored=0
                stored=stored if stored in vals else 0
                val=col.selectbox(f"{label} {side}",vals,index=vals.index(stored),
                    format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{fk}",label_visibility="collapsed")
                collected[fk]=val
        collected["ashworth_notes"]=st.text_area("Notes",value=lv("ashworth_notes",""),height=60,key=f"{key_prefix}_ash_notes")
        return collected
    @classmethod
    def score(cls,data):
        vals=[]
        for k,_ in cls.MUSCLES:
            for side in ["_d","_g"]:
                try: vals.append(float(data.get(f"{k}{side}",0) or 0))
                except: pass
        if not vals: return {"score":None,"interpretation":"","color":"#888","details":{}}
        mx=max(vals)
        color="#388e3c" if mx<=1 else "#f57c00" if mx<=2 else "#d32f2f"
        return {"score":mx,"interpretation":f"Max:{mx}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data): return bool(data.get("ashworth_notes","") or any(data.get(f"{k}_d","") for k,_ in cls.MUSCLES))
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        st.info("Évolution Ashworth : consultez les tableaux de données pour le suivi par muscle.")
        import pandas as pd
        rows=[]
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            r={"Bilan":lbl}
            for k,m in cls.MUSCLES:
                r[f"{m} D"]=row.get(f"{k}_d","—"); r[f"{m} G"]=row.get(f"{k}_g","—")
            rows.append(r)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
