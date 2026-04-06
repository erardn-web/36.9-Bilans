"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class IKDC(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"ikdc","nom":"IKDC — Genou","tab_label":"📊 IKDC","categorie":"questionnaire",
                "tags":["genou","LCA","fonctionnel","ligament"],
                "description":"International Knee Documentation Committee — score fonctionnel genou /100"}
    @classmethod
    def fields(cls): return [f"ikdc_q{i}" for i in range(1,11)]+["ikdc_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📊 IKDC — Genou</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">10 questions sur la fonction du genou. Score 0 = incapacité maximale · 100 = aucune limitation.</div>', unsafe_allow_html=True)
        collected={}
        questions=[
            ("ikdc_q1","Quelle est l'activité la plus intense que vous puissiez pratiquer sans douleur sévère ?",[
                (0,"Pas d'activité physique"),(1,"Activités légères (marche, ménage)"),(2,"Activités modérées (nage, vélo)"),
                (3,"Activités intenses (jogging, tennis)"),(4,"Activités très intenses (saut, pivotement)")]),
            ("ikdc_q2","À quelle fréquence votre genou est-il douloureux ?",[
                (0,"Constamment"),(2,"Quotidiennement"),(4,"Hebdomadairement"),(6,"Mensuellement"),(8,"Jamais")]),
            ("ikdc_q3","Si vous avez de la douleur, quelle est son intensité ?",[
                (0,"10/10 — Extrême"),(2,"7-9/10 — Sévère"),(4,"4-6/10 — Modérée"),(6,"1-3/10 — Légère"),(8,"Aucune douleur")]),
            ("ikdc_q4","Quelle est la rigidité de votre genou ?",[
                (0,"Extrême"),(2,"Sévère"),(4,"Modérée"),(6,"Légère"),(8,"Aucune")]),
            ("ikdc_q5","Quel gonflement avez-vous dans le genou ?",[
                (0,"Extrême"),(2,"Sévère"),(4,"Modéré"),(6,"Léger"),(8,"Aucun")]),
            ("ikdc_q6","Votre genou est-il instable (dérobements) ?",[
                (0,"Constamment"),(2,"Souvent"),(4,"Parfois"),(6,"Rarement"),(8,"Jamais")]),
            ("ikdc_q7","À quelle activité êtes-vous limité(e) ?",[
                (0,"Incapable de travailler"),(2,"Seulement travail léger"),(4,"Travail modéré"),(6,"Toutes activités quotidiennes"),(8,"Aucune limitation")]),
            ("ikdc_q8","Quelle activité sportive ?",[
                (0,"Aucune"),(2,"Activités légères"),(4,"Activités modérées"),(6,"Sport intensif non compétitif"),(8,"Compétition à niveau habituel")]),
            ("ikdc_q9","Comment évaluez-vous votre genou ?",[
                (0,"Très mauvais"),(2,"Mauvais"),(4,"Moyen"),(6,"Bon"),(8,"Normal")]),
            ("ikdc_q10","Quelle note sur 10 donneriez-vous à votre genou ?",[
                (0,"0-2"),(2,"3-4"),(4,"5-6"),(6,"7-8"),(8,"9-10")]),
        ]
        total=0
        for k,label,opts in questions:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[o[0] for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if s==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{k}",horizontal=True)
            collected[k]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        score=round(total/0.8)
        collected["ikdc_score"]=min(score,100)
        color="#388e3c" if score>=75 else "#f57c00" if score>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">IKDC : {min(score,100)}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("ikdc_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=75 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("ikdc_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("ikdc_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="IKDC",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="IKDC /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"IKDC":r.get("ikdc_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── CSI Central Sensitization Inventory ──────────────────────────────────────
@register_test
class CSI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"csi","nom":"CSI — Sensibilisation centrale","tab_label":"⚡ CSI","categorie":"questionnaire",
                "tags":["sensibilisation centrale","douleur chronique","psychosocial"],
                "description":"Central Sensitization Inventory — 25 items /100. Seuil ≥ 40"}
    @classmethod
    def fields(cls): return [f"csi_q{i}" for i in range(1,26)]+["csi_score"]
    CSI_QUESTIONS=[
        "Je ressens de la douleur dans tout mon corps","Je manque d'énergie",
        "J'ai des troubles du sommeil","Je souffre de raideurs musculaires",
        "Je souffre de difficultés de concentration","J'ai la peau sensible au toucher",
        "Je me sens stressé(e)","Je ressens de la douleur au moindre effort",
        "Je ressens de la douleur qui brûle","Je souffre de maux de tête",
        "J'ai besoin d'uriner souvent","Mes jambes se contractent ou font des spasmes",
        "J'ai du mal à m'endormir ou à rester endormi","J'ai du mal à rester assis longtemps",
        "Je me sens anxieux(se)","Je souffre d'inconfort pelvien",
        "J'ai des indigestions ou le ventre irritable","Je suis fatigué(e)",
        "J'ai des troubles de l'humeur","Je souffre de maux de tête derrière la tête",
        "Ma vision est parfois floue","Je souffre de nausées",
        "Je souffre de sensibilité à la lumière","Mes pieds/mains sont engourdis",
        "J'ai des difficultés à avaler",
    ]
    OPTS=["0 — Jamais","1 — Rarement","2 — Parfois","3 — Souvent","4 — Toujours"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">⚡ CSI — Inventaire de sensibilisation centrale</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = jamais · 4 = toujours. Score ≥ 40 : sensibilisation centrale probable.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.CSI_QUESTIONS,1):
            k=f"csi_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(q,[0,1,2,3,4],index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["csi_score"]=total
        color="#d32f2f" if total>=53 else "#f57c00" if total>=40 else "#388e3c"
        msg="Sévère" if total>=53 else "Modérée" if total>=40 else "Légère/Absente"
        st.markdown(f'<div class="score-box" style="background:{color}">CSI : {total}/100 — Sensibilisation {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("csi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=53 else "#f57c00" if s>=40 else "#388e3c"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("csi_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("csi_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="CSI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=40,line_dash="dot",line_color="#f57c00",annotation_text="Seuil sensibilisation ≥40")
        fig.update_layout(yaxis=dict(range=[0,105],title="CSI /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"CSI":r.get("csi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── QBPDS Quebec Back Pain Disability Scale ───────────────────────────────────
@register_test
class QBPDS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"qbpds","nom":"QBPDS — Incapacité lombaire","tab_label":"📋 QBPDS","categorie":"questionnaire",
                "tags":["lombalgie","incapacité","dos","fonctionnel"],
                "description":"Quebec Back Pain Disability Scale — 20 items /100"}
    @classmethod
    def fields(cls): return [f"qbpds_q{i}" for i in range(1,21)]+["qbpds_score"]
    QBPDS_QUESTIONS=[
        "Se lever du lit","Rester au lit toute la nuit","Se retourner dans le lit",
        "Aller en voiture","Se tenir debout 20-30 min","S'asseoir dans une chaise 1h",
        "Monter une volée d'escaliers","Marcher 300-400 m","Marcher plusieurs kilomètres",
        "Atteindre les hautes étagères","Lancer un ballon","Courir 100 m",
        "Enlever la nourriture du réfrigérateur","Faire son lit","Mettre des chaussettes",
        "Se plier pour ramasser un objet","Tirer/pousser une porte","Porter deux sacs d'épicerie",
        "Soulever et porter une valise lourde","Porter un enfant",
    ]
    OPTS=["0 — Pas difficile","1 — Minimum","2 — Peu","3 — Modérément","4 — Très","5 — Extrêmement"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📋 QBPDS — Incapacité lombaire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = pas difficile · 5 = extrêmement difficile. Score /100.</div>', unsafe_allow_html=True)
        collected={}; total=0
        cols=st.columns(2)
        for i,q in enumerate(self.QBPDS_QUESTIONS,1):
            k=f"qbpds_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=cols[(i-1)%2].selectbox(q,list(range(6)),index=stored,format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["qbpds_score"]=total
        color="#388e3c" if total<=20 else "#f57c00" if total<=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">QBPDS : {total}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("qbpds_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=20 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("qbpds_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("qbpds_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="QBPDS",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="QBPDS /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"QBPDS":r.get("qbpds_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── ATRS Achilles Tendon Total Rupture Score ──────────────────────────────────
@register_test
class ATRS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"atrs","nom":"ATRS — Rupture tendon Achille","tab_label":"🦶 ATRS","categorie":"questionnaire",
                "tags":["achille","rupture","tendon","cheville","post-chirurgical"],
                "description":"Achilles Tendon Total Rupture Score — 10 items /100"}
    @classmethod
    def fields(cls): return [f"atrs_q{i}" for i in range(1,11)]+["atrs_score"]
    QUESTIONS=[
        "Limitation en raison de la faiblesse du tendon",
        "Limitation en raison de la fatigue du tendon",
        "Limitation en raison de la raideur du tendon",
        "Limitation en raison de la douleur",
        "Difficulté à marcher sur terrain inégal",
        "Difficulté à courir",
        "Difficulté à prendre le départ en sprint",
        "Difficulté à sauter",
        "Difficulté à pratiquer du sport",
        "Difficulté à pratiquer des activités physiques lourdes",
    ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦶 ATRS — Tendon Achille (rupture)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = limitation maximale · 10 = aucune limitation. Score /100.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"atrs_q{i}"
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 5
            except: v=5
            val=st.slider(q,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["atrs_score"]=total
        color="#388e3c" if total>=80 else "#f57c00" if total>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">ATRS : {total}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("atrs_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=80 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("atrs_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("atrs_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ATRS",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="ATRS /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ATRS":r.get("atrs_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── WOSI Western Ontario Shoulder Instability ─────────────────────────────────
@register_test
class WOSI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"wosi","nom":"WOSI — Instabilité épaule","tab_label":"💪 WOSI","categorie":"questionnaire",
                "tags":["épaule","instabilité","sport","fonctionnel"],
                "description":"Western Ontario Shoulder Instability Index — 21 items, impact instabilité épaule"}
    @classmethod
    def fields(cls): return [f"wosi_q{i}" for i in range(1,22)]+["wosi_score","wosi_pct"]
    QUESTIONS=[
        "Douleur physique lors d'activités au-dessus de la tête","Douleur lors d'activités avec force",
        "Douleur lors d'activités de sport ou loisirs","Faiblesse musculaire",
        "Fatigue à l'épaule","Cliquet ou craquements","Instabilité/sensation d'épaule qui cède",
        "Compensation d'autres muscles","Perte d'amplitude","Raideur matinale",
        "Gêne pour travailler","Peur de tomber sur l'épaule","Peur de se réinstabiliser",
        "Difficulté à dormir","Difficulté à soulever des objets lourds","Difficulté à soulever des objets légers",
        "Difficulté à pratiquer votre sport","Pas au niveau habituel","Conscience du problème",
        "Impact sur confiance","Impact vie quotidienne",
    ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 WOSI — Instabilité épaule</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Évaluez l\'impact de votre épaule sur chaque item (0 = aucun impact · 100 = impact maximal).</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"wosi_q{i}"
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=st.slider(q,0,100,v,step=5,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        pct=round((1-(total/2100))*100,1)
        collected.update({"wosi_score":total,"wosi_pct":pct})
        color="#388e3c" if pct>=75 else "#f57c00" if pct>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">WOSI : {pct:.0f}% (score brut: {total}/2100)</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("wosi_pct",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=75 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}%","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("wosi_pct",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("wosi_pct","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="WOSI",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="WOSI %"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"WOSI %":r.get("wosi_pct","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
