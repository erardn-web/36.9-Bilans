"""tests/questionnaires/roland_morris.py — Roland-Morris Disability Questionnaire"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

RMQ_ITEMS = [
    ("rmq_q1","Je reste à la maison la plupart du temps à cause de mon mal de dos"),
    ("rmq_q2","Je change souvent de position pour soulager mon dos"),
    ("rmq_q3","Je marche plus lentement que d'habitude à cause de mon dos"),
    ("rmq_q4","À cause de mon dos, je ne fais pas les tâches habituelles à la maison"),
    ("rmq_q5","À cause de mon dos, je m'aide de la rampe pour monter les escaliers"),
    ("rmq_q6","À cause de mon dos, je m'allonge plus souvent pour me reposer"),
    ("rmq_q7","À cause de mon dos, je dois m'appuyer sur quelque chose pour me lever d'un fauteuil"),
    ("rmq_q8","À cause de mon dos, j'essaie d'obtenir l'aide d'autrui pour faire des choses"),
    ("rmq_q9","À cause de mon dos, je m'habille plus lentement que d'habitude"),
    ("rmq_q10","Je ne reste debout que pour de courtes périodes à cause de mon dos"),
    ("rmq_q11","À cause de mon dos, j'essaie de ne pas me baisser ni m'agenouiller"),
    ("rmq_q12","J'ai du mal à me lever d'une chaise à cause de mon dos"),
    ("rmq_q13","Mon dos me fait mal presque tout le temps"),
    ("rmq_q14","J'ai du mal à me retourner dans mon lit à cause de mon dos"),
    ("rmq_q15","Mon appétit n'est pas très bon à cause de mon dos"),
    ("rmq_q16","J'ai du mal à mettre mes chaussettes (ou collants) à cause de mon dos"),
    ("rmq_q17","Je ne marche que de courtes distances à cause de mon dos"),
    ("rmq_q18","Je dors moins bien à cause de mon dos"),
    ("rmq_q19","À cause de mon dos, je m'habille avec l'aide d'autrui"),
    ("rmq_q20","Je reste assis la majeure partie de la journée à cause de mon dos"),
    ("rmq_q21","J'évite les travaux pénibles à la maison à cause de mon dos"),
    ("rmq_q22","À cause de mon dos, je suis plus irritable et de mauvaise humeur que d'habitude"),
    ("rmq_q23","À cause de mon dos, je monte les escaliers plus lentement que d'habitude"),
    ("rmq_q24","Je reste au lit la majeure partie de la journée à cause de mon dos"),
]


def _rmq_interp(score):
    if score<=4: return "Incapacité minime"
    if score<=14: return "Incapacité modérée"
    return "Incapacité sévère"


@register_test
class RolandMorris(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"roland_morris","nom":"Roland-Morris — Lombalgie","tab_label":"📋 Roland-Morris","categorie":"questionnaire",
                "tags":["lombalgie","incapacité","dos","fonctionnel"],
                "description":"Roland-Morris Disability Questionnaire — 24 items oui/non, /24"}

    @classmethod
    def fields(cls):
        return [k for k,_ in RMQ_ITEMS]+["rmq_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📋 Roland-Morris — Incapacité lombaire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Cochez les phrases qui décrivent votre situation aujourd\'hui. Score 0 = pas d\'incapacité · 24 = incapacité maximale.</div>', unsafe_allow_html=True)
        collected={}; total=0
        cols=st.columns(2)
        for i,(k,label) in enumerate(RMQ_ITEMS):
            raw=lv(k,None)
            stored = raw == "1" or raw == "True" or raw == 1
            val=cols[i%2].checkbox(label,value=stored,key=f"{key_prefix}_{k}")
            collected[k]=1 if val else 0
            if val: total+=1
        collected["rmq_score"]=total
        color="#388e3c" if total<=4 else "#f57c00" if total<=14 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Roland-Morris : {total}/24 — {_rmq_interp(total)}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("rmq_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=4 else "#f57c00" if s<=14 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/24 — {_rmq_interp(s)}","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("rmq_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("rmq_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Roland-Morris",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        for y,c,l in [(4,"#388e3c","≤4 minime"),(14,"#f57c00","≤14 modérée")]:
            fig.add_hline(y=y,line_dash="dot",line_color=c,annotation_text=l,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,26],title="Score /24"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Roland-Morris":r.get("rmq_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
