"""tests/questionnaires/neurologie.py — Barthel, 10MWT, Ashworth, Fugl-Meyer"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Barthel Index ─────────────────────────────────────────────────────────────
@register_test
class Barthel(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"barthel","nom":"Barthel — Indépendance fonctionnelle","tab_label":"🏥 Barthel",
                "categorie":"questionnaire","tags":["neurologie","AVC","indépendance","AVQ","rééducation"],
                "description":"Barthel Index — 10 AVQ, indépendance fonctionnelle 0-100"}
    ITEMS=[
        ("barthel_alimentation","Alimentation",[(10,"Indépendant"),(5,"Aide partielle"),(0,"Dépendant")]),
        ("barthel_bain","Bain/douche",[(5,"Indépendant"),(0,"Dépendant")]),
        ("barthel_toilette","Toilette/hygiène",[(5,"Indépendant"),(0,"Dépendant")]),
        ("barthel_habillage","Habillage",[(10,"Indépendant"),(5,"Aide partielle"),(0,"Dépendant")]),
        ("barthel_continence_intestin","Continence intestinale",[(10,"Continence complète"),(5,"Accidents occasionnels"),(0,"Incontinence")]),
        ("barthel_continence_vesicale","Continence vésicale",[(10,"Continence complète"),(5,"Accidents occasionnels"),(0,"Incontinence")]),
        ("barthel_toilettes","Utilisation des toilettes",[(10,"Indépendant"),(5,"Aide partielle"),(0,"Dépendant")]),
        ("barthel_transferts","Transferts lit-fauteuil",[(15,"Indépendant"),(10,"Aide mineure"),(5,"Aide importante"),(0,"Incapable")]),
        ("barthel_marche","Déambulation",[(15,"Indépendant >50m"),(10,"Aide 50m"),(5,"Fauteuil roulant indépendant"),(0,"Immobile")]),
        ("barthel_escaliers","Escaliers",[(10,"Indépendant"),(5,"Aide"),(0,"Incapable")]),
    ]
    def _interp(self,s):
        if s>=95: return "Indépendant"
        if s>=75: return "Dépendance légère"
        if s>=50: return "Dépendance modérée"
        if s>=25: return "Dépendance sévère"
        return "Dépendance totale"
    @classmethod
    def fields(cls): return [k for k,*_ in cls.ITEMS]+["barthel_score"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏥 Index de Barthel — Indépendance fonctionnelle</div>', unsafe_allow_html=True)
        collected={}; total=0
        for field,label,opts in self.ITEMS:
            raw=lv(field,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[o[0] for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if s==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{field}",horizontal=True)
            collected[field]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["barthel_score"]=total
        color="#388e3c" if total>=95 else "#f57c00" if total>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Barthel : {total}/100 — {self._interp(total)}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("barthel_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=95 else "#f57c00" if s>=50 else "#d32f2f"
        interps=[(95,"Indépendant"),(75,"Légère"),(50,"Modérée"),(25,"Sévère"),(0,"Totale")]
        interp=next(l for t,l in interps if s>=t)
        return {"score":s,"interpretation":f"{s:.0f}/100 — {interp}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("barthel_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("barthel_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Barthel",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        for y,c,l in [(95,"#388e3c","Indépendant"),(75,"#7cb87e","Légère"),(50,"#f57c00","Modérée")]:
            fig.add_hline(y=y,line_dash="dot",line_color=c,annotation_text=l,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="Barthel /100"),height=320,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Barthel":r.get("barthel_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── 10-Metre Walk Test ────────────────────────────────────────────────────────