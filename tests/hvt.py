"""
tests/tests_cliniques/hvt.py — Test HVT (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import (
    HVT_DESCRIPTION, HVT_SYMPTOMES, HVT_PHASES, HVT_PARAMS
)


def _safe_float(v):
    try: return float(v) if v not in (None,"","None") else None
    except: return None


@register_test
class HVT(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"hvt","nom":"Test d'hyperventilation","tab_label":"🌬️ Test HV",
                "categorie":"test_clinique","tags":["hyperventilation", "SHV", "respiratoire", "test", "provocation"],"description":"Test HVT — grille PetCO₂/FR/SpO₂/FC"}

    @classmethod
    def fields(cls):
        fields = []
        for phase_key,_,times in HVT_PHASES:
            for t in times:
                for p_key,*_ in HVT_PARAMS:
                    fields.append(f"hvt_{phase_key}_{t}_{p_key}")
        return fields + ["hvt_symptomes_reproduits","hvt_symptomes_list",
                         "hvt_duree_retour","hvt_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🌬️ Test d\'hyperventilation volontaire</div>',
                    unsafe_allow_html=True)
        st.markdown(HVT_DESCRIPTION)

        # ── Grille de mesures ─────────────────────────────────────────────────
        st.markdown("#### 📊 Grille de mesures")
        st.markdown(
            '<div class="info-box">Entrez les valeurs mesurées à chaque temps. '
            'Laissez vide si non mesuré.</div>', unsafe_allow_html=True)

        hvt_grid = {}
        for phase_key, phase_label, times in HVT_PHASES:
            st.markdown(f"**{phase_label}**")
            col_headers = st.columns([1.2] + [1]*len(HVT_PARAMS))
            col_headers[0].markdown("**Temps**")
            for j,(p_key,p_label,*_) in enumerate(HVT_PARAMS):
                col_headers[j+1].markdown(f"**{p_label}**")

            for t in times:
                row_cols = st.columns([1.2] + [1]*len(HVT_PARAMS))
                row_cols[0].markdown(
                    f"<small>{'T0' if t==0 else f'{t} min'}</small>",
                    unsafe_allow_html=True)
                for j,(p_key,p_label,*_) in enumerate(HVT_PARAMS):
                    cell_key = f"hvt_{phase_key}_{t}_{p_key}"
                    stored   = lv(cell_key, "")
                    display  = str(int(_safe_float(stored))) if _safe_float(stored) else ""
                    entered  = row_cols[j+1].text_input(
                        label="", value=display,
                        key=f"{key_prefix}_grid_{cell_key}",
                        label_visibility="collapsed", placeholder="—")
                    try:    hvt_grid[cell_key] = int(float(entered)) if entered.strip() else ""
                    except: hvt_grid[cell_key] = ""
            st.markdown("---")

        # ── Graphique ─────────────────────────────────────────────────────────
        st.markdown("#### 📈 Visualisation")
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        all_times_labels = ["T0","R1'","R2'","R3'","HV1'","HV2'","HV3'",
                            "Rec1'","Rec2'","Rec3'","Rec4'","Rec5'"]
        all_keys = ([(  "repos",t) for t in [0,1,2,3]] +
                    [("hv",    t) for t in [1,2,3]] +
                    [("rec",   t) for t in [1,2,3,4,5]])

        fig = make_subplots(rows=2,cols=2,
            subplot_titles=["PetCO₂ (mmHg)","FR (cyc/min)","SpO₂ (%)","FC (bpm)"],
            shared_xaxes=False)
        param_pos = [("petco2",1,1,"#1a3c5e"),("fr",1,2,"#f57c00"),
                     ("spo2",2,1,"#388e3c"),("fc",2,2,"#7b1fa2")]

        for p_key,r,c,color in param_pos:
            y_vals = []
            for ph_key,t in all_keys:
                k = f"hvt_{ph_key}_{t}_{p_key}"
                v = hvt_grid.get(k) or lv(k,"")
                try:    y_vals.append(float(v) if v else None)
                except: y_vals.append(None)
            fig.add_trace(go.Scatter(x=all_times_labels,y=y_vals,mode="lines+markers",
                line=dict(color=color,width=2.5),marker=dict(size=8),
                showlegend=False,connectgaps=False),row=r,col=c)
            for sep in [3.5,6.5]:
                fig.add_vline(x=sep,line_dash="dot",line_color="grey",line_width=1,row=r,col=c)

        fig.add_hline(y=35,line_dash="dot",line_color="#d32f2f",annotation_text="35 mmHg",row=1,col=1)
        fig.add_hline(y=45,line_dash="dot",line_color="#388e3c",annotation_text="45 mmHg",row=1,col=1)
        fig.add_hline(y=95,line_dash="dot",line_color="#f57c00",annotation_text="95%",row=2,col=1)
        fig.update_layout(height=500,plot_bgcolor="white",margin=dict(t=40,b=20))
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig,use_container_width=True)

        # ── Résultat global ───────────────────────────────────────────────────
        st.markdown("#### 🏁 Résultat global")
        col1, col2 = st.columns(2)
        hvt_opts = ["Non réalisé","Oui ✅","Partiellement ⚠️","Non ❌"]
        stored_rep = lv("hvt_symptomes_reproduits","Non réalisé")
        rep_idx    = hvt_opts.index(stored_rep) if stored_rep in hvt_opts else 0
        with col1:
            hvt_reproduits = st.radio(
                "Le test reproduit-il les symptômes habituels ?",
                hvt_opts, index=rep_idx, key=f"{key_prefix}_hvt_rep")
        with col2:
            stored_duree = lv("hvt_duree_retour",None)
            try:    default_duree = int(float(stored_duree)) if stored_duree not in (None,"","None") else None
            except: default_duree = None
            hvt_duree = st.number_input(
                "Temps de retour à la normale (minutes)",
                min_value=0, max_value=60,
                value=default_duree, step=1,
                key=f"{key_prefix}_hvt_duree")

        existing_symp = str(lv("hvt_symptomes_list","") or "").split("|")
        symp_sel = st.multiselect("Symptômes reproduits :",HVT_SYMPTOMES,
            default=[s for s in existing_symp if s in HVT_SYMPTOMES],
            key=f"{key_prefix}_hvt_symp")

        hvt_notes = st.text_area("Observations / notes cliniques",
            value=str(lv("hvt_notes","") or ""),height=100,
            key=f"{key_prefix}_hvt_notes")

        if "Oui ✅" in hvt_reproduits:
            st.markdown(
                '<div class="success-box">✅ <strong>Test positif</strong> — '
                'Confirme le diagnostic de SHV.</div>',unsafe_allow_html=True)
        elif "Partiellement" in hvt_reproduits:
            st.markdown(
                '<div class="warn-box">⚠️ <strong>Test partiellement positif</strong> — '
                'Arguments en faveur d\'un SHV.</div>',unsafe_allow_html=True)

        collected = {
            "hvt_symptomes_reproduits": hvt_reproduits,
            "hvt_symptomes_list":       "|".join(symp_sel),
            "hvt_duree_retour":         hvt_duree if hvt_duree else "",
            "hvt_notes":                hvt_notes,
            **hvt_grid,
        }
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        for phase_key,_,times in HVT_PHASES:
            for t in times:
                v = bilan_data.get(f"hvt_{phase_key}_{t}_petco2","")
                if str(v).strip() not in ("","0","None","nan"): return True
        return False
