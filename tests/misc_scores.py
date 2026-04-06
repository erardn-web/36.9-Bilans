"""tests/questionnaires/misc_scores.py — Cumberland CAIT, IKDC, Tegner, DHI, HIT-6"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Cumberland Ankle Instability Tool (CAIT) ──────────────────────────────────
@register_test
class CAIT(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"cait","nom":"CAIT — Instabilité cheville","tab_label":"🦶 CAIT","categorie":"questionnaire",
                "tags":["cheville","instabilité","entorse","fonctionnel"],
                "description":"Cumberland Ankle Instability Tool — 9 items /30. Seuil instabilité ≤ 27"}
    @classmethod
    def fields(cls): return [f"cait_q{i}" for i in range(1,10)]+["cait_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦶 CAIT — Instabilité de cheville</div>', unsafe_allow_html=True)
        collected={}; total=0
        questions=[
            ("cait_q1","Douleur à la cheville",[("4","Jamais"),("3","Pendant le sport"),("2","En courant sur terrain inégal"),("1","En courant sur terrain plat"),("0","En marchant")]),
            ("cait_q2","Instabilité (genou qui cède)",[("4","Jamais"),("3","Parfois pendant sport (pas à chaque fois)"),("2","Souvent pendant sport"),("1","Parfois dans AVQ"),("0","Souvent dans AVQ")]),
            ("cait_q3","Sensation de cheville qui 'tourne'",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q4","Instabilité en virage serré",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q5","Descendre les escaliers",[("3","Jamais"),("2","Parfois"),("1","Souvent"),("0","Toujours")]),
            ("cait_q6","Tenir en équilibre sur une jambe",[("2","Jamais, >10s"),("1","Parfois"),("0","Souvent")]),
            ("cait_q7","Instabilité en sautant d'une seule jambe",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
            ("cait_q8","Instabilité en sautant en hauteur",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
            ("cait_q9","Instabilité en courant sur terrain inégal",[("2","Jamais"),("1","Parfois"),("0","Souvent")]),
        ]
        for k,label,opts in questions:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[int(o[0]) for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if int(s)==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["cait_score"]=total
        color="#d32f2f" if total<=27 else "#388e3c"
        msg="Instabilité fonctionnelle" if total<=27 else "Cheville stable"
        st.markdown(f'<div class="score-box" style="background:{color}">CAIT : {total}/30 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("cait_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s<=27 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/30","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("cait_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("cait_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="CAIT",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=27,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil instabilité ≤27")
        fig.update_layout(yaxis=dict(range=[0,32],title="CAIT /30"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"CAIT":r.get("cait_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Tegner Activity Scale ─────────────────────────────────────────────────────
@register_test
class Tegner(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tegner","nom":"Tegner — Niveau d'activité","tab_label":"🏅 Tegner","categorie":"questionnaire",
                "tags":["genou","activité","sport","LCA","niveau fonctionnel"],
                "description":"Tegner Activity Scale — niveau d'activité 0-10 avant blessure et actuel"}
    @classmethod
    def fields(cls): return ["tegner_avant","tegner_actuel"]
    OPTS={0:"0 — Incapacité au travail ou pension invalidité",1:"1 — Travail sédentaire",
          2:"2 — Travail léger (marche sur terrain inégal impossible)",3:"3 — Travail léger (marche possible), natation",
          4:"4 — Travail modérément lourd, ski fond, vélo, jogging",5:"5 — Travail lourd, compétition cyclisme, ski alpin",
          6:"6 — Sport loisir : tennis, badminton, hand, basket, ski",7:"7 — Compétition : tennis, athlétisme, motocross, hand, basket",
          8:"8 — Compétition : squash, badminton ou ski alpin de compétition",9:"9 — Compétition : football (D3/D4), hockey sur glace",
          10:"10 — Compétition nationale/internationale football"}

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏅 Tegner — Niveau d\'activité</div>', unsafe_allow_html=True)
        collected={}
        for k,label in [("tegner_avant","Niveau avant blessure"),("tegner_actuel","Niveau actuel")]:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 5
            except: stored=5
            val=st.selectbox(label,list(self.OPTS.keys()),index=stored,format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{k}")
            collected[k]=val
        diff=collected["tegner_actuel"]-collected["tegner_avant"]
        color="#388e3c" if diff>=0 else "#f57c00" if diff>=-2 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Avant: {collected["tegner_avant"]}/10 | Actuel: {collected["tegner_actuel"]}/10 | Diff: {diff:+d}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("tegner_actuel",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=7 else "#f57c00" if s>=4 else "#d32f2f"
        return {"score":s,"interpretation":f"Actuel:{s:.0f}/10","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data): return str(data.get("tegner_actuel","")).strip() not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("tegner_avant","Avant","#aaa"),("tegner_actuel","Actuel","#2B57A7")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,11],title="Tegner /10"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Avant":r.get("tegner_avant","—"),"Actuel":r.get("tegner_actuel","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── DHI Dizziness Handicap Inventory ─────────────────────────────────────────
@register_test
class DHI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"dhi","nom":"DHI — Vertiges","tab_label":"🌀 DHI","categorie":"questionnaire",
                "tags":["vertiges","vestibulaire","équilibre","VPPB"],
                "description":"Dizziness Handicap Inventory — 25 items /100, impact des vertiges"}
    @classmethod
    def fields(cls): return [f"dhi_q{i}" for i in range(1,26)]+["dhi_score","dhi_physique","dhi_emotionnel","dhi_fonctionnel"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🌀 DHI — Inventaire du handicap lié aux vertiges</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">25 questions — Oui (4 pts) / Parfois (2 pts) / Non (0 pt). Score 0 = pas de handicap · 100 = handicap maximal.</div>', unsafe_allow_html=True)
        from collections import defaultdict
        collected={}; scores=defaultdict(int)
        subs={1:"P",2:"E",3:"F",4:"P",5:"F",6:"F",7:"P",8:"E",9:"P",10:"F",
              11:"E",12:"F",13:"P",14:"F",15:"E",16:"F",17:"P",18:"E",19:"P",20:"P",
              21:"E",22:"F",23:"E",24:"F",25:"F"}
        labels_q=[
            "Votre problème de vertige vous fait-il regarder où vous posez les pieds ?",
            "Votre problème de vertige est-il déprimant pour vous ?",
            "Est-ce que votre problème de vertige vous prive de voyages d'affaires ou de loisirs ?",
            "Marcher dans les allées d'un supermarché aggrave-t-il votre vertige ?",
            "Votre problème de vertige vous complique-t-il l'entrée/sortie du lit ?",
            "Votre problème de vertige vous contraint-il à limiter vos activités sociales ?",
            "Le fait de regarder en l'air aggrave-t-il votre problème de vertige ?",
            "Votre problème de vertige vous prive-t-il d'assumer plus de responsabilités ?",
            "Votre problème de vertige aggrave-t-il votre difficulté lors de promenades seul(e) ?",
            "Votre problème de vertige a-t-il un retentissement sur vos activités professionnelles/ménagères ?",
            "Avez-vous honte de votre problème de vertige devant autrui ?",
            "Votre problème de vertige vous prive-t-il de visiter des amis ou de la famille ?",
            "En raison de votre vertige, pouvez-vous décrire votre démarche comme titubante ?",
            "Votre problème de vertige rend-il difficile des sports ou activités physiques intenses ?",
            "Votre problème de vertige vous déprime-t-il parfois ?",
            "Votre problème de vertige vous complique-t-il les promenades seul(e) ?",
            "Marcher sur le trottoir aggrave-t-il votre vertige ?",
            "En raison de votre problème de vertige, est-il difficile pour vous de vous concentrer ?",
            "En raison de votre problème de vertige, est-il difficile de marcher dans votre maison la nuit ?",
            "Votre problème de vertige vous prive-t-il de rester seul(e) à la maison ?",
            "Votre problème de vertige vous fait-il vous sentir handicapé(e) ?",
            "Votre problème de vertige vous complique-t-il les relations avec votre famille et vos amis ?",
            "Avez-vous quelquefois des épisodes de dépression en raison de votre vertige ?",
            "Votre problème de vertige aggrave-t-il vos activités professionnelles ?",
            "En vous penchant en avant, votre problème de vertige aggrave-t-il votre vertige ?",
        ]
        total=0
        for i,q_label in enumerate(labels_q,1):
            k=f"dhi_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(q_label,[0,2,4],index=[0,2,4].index(stored) if stored in [0,2,4] else 0,
                format_func=lambda x:{0:"Non (0)",2:"Parfois (2)",4:"Oui (4)"}[x],
                horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val; scores[subs[i]]+=val
        collected.update({"dhi_score":total,"dhi_physique":scores["P"],"dhi_emotionnel":scores["E"],"dhi_fonctionnel":scores["F"]})
        color="#388e3c" if total<=16 else "#f57c00" if total<=36 else "#d32f2f"
        msg="Léger" if total<=16 else "Moyen" if total<=36 else "Sévère"
        st.markdown(f'<div class="score-box" style="background:{color}">DHI : {total}/100 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("dhi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=16 else "#f57c00" if s<=36 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("dhi_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("dhi_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="DHI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=16,line_dash="dot",line_color="#388e3c",annotation_text="≤16 léger")
        fig.add_hline(y=36,line_dash="dot",line_color="#f57c00",annotation_text="≤36 moyen")
        fig.update_layout(yaxis=dict(range=[0,105],title="DHI /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"DHI":r.get("dhi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── HIT-6 Headache Impact Test ────────────────────────────────────────────────
@register_test
class HIT6(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"hit6","nom":"HIT-6 — Impact des céphalées","tab_label":"🤕 HIT-6","categorie":"questionnaire",
                "tags":["céphalées","migraines","tête","impact","incapacité"],
                "description":"Headache Impact Test-6 — 6 items, impact des maux de tête /78"}
    @classmethod
    def fields(cls): return [f"hit6_q{i}" for i in range(1,7)]+["hit6_score"]
    OPTS={"never":6,"rarely":8,"sometimes":10,"very_often":11,"always":13}
    OPTS_FR={"never":"Jamais (6)","rarely":"Rarement (8)","sometimes":"Parfois (10)","very_often":"Très souvent (11)","always":"Toujours (13)"}
    QUESTIONS=[
        "Quand vous avez des maux de tête, leur intensité est-elle sévère ?",
        "Vos maux de tête vous empêchent-ils de mener à bien vos activités quotidiennes ?",
        "Vous arrive-t-il de souhaiter vous allonger à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, vous êtes-vous senti(e) trop fatigué(e) à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, avez-vous eu envie de ne rien faire de spécial à cause de vos maux de tête ?",
        "Au cours des 4 dernières semaines, avez-vous trouvé vos capacités de concentration limitées à cause de vos maux de tête ?",
    ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🤕 HIT-6 — Impact des céphalées</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"hit6_q{i}"
            raw=lv(k,"never")
            stored=raw if raw in self.OPTS else "never"
            val=st.selectbox(q,list(self.OPTS_FR.keys()),index=list(self.OPTS.keys()).index(stored),
                format_func=lambda x:self.OPTS_FR[x],key=f"{key_prefix}_{k}")
            collected[k]=val; total+=self.OPTS[val]
        collected["hit6_score"]=total
        color="#d32f2f" if total>=60 else "#f57c00" if total>=56 else "#388e3c"
        msg="Impact sévère" if total>=60 else "Impact substantiel" if total>=56 else "Impact moindre"
        st.markdown(f'<div class="score-box" style="background:{color}">HIT-6 : {total}/78 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("hit6_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=60 else "#f57c00" if s>=56 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/78","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("hit6_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("hit6_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="HIT-6",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=56,line_dash="dot",line_color="#f57c00",annotation_text="Impact substantiel ≥56")
        fig.add_hline(y=60,line_dash="dot",line_color="#d32f2f",annotation_text="Impact sévère ≥60")
        fig.update_layout(yaxis=dict(range=[36,80],title="HIT-6 /78"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"HIT-6":r.get("hit6_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
