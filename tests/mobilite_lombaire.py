"""tests/tests_cliniques/mobilite_lombaire.py — Mobilité lombaire (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

MOB_OPTS = ["— Non renseigné —","1/3","2/3","3/3"]
MOB_NUM  = {"1/3":1,"2/3":2,"3/3":3}

@register_test
class MobiliteLombaire(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"mobilite_lombaire","nom":"Mobilité rachis lombaire",
                "tab_label":"📐 Mobilité rachis lombaire","categorie":"test_clinique","tags":["lombalgie", "rachis", "mobilité", "schober"],
                "description":"Schober, amplitudes rachis lombaire (1/3, 2/3, 3/3)"}

    @classmethod
    def fields(cls):
        return ["o_schober","o_flexion_cm","o_extension_mob",
                "o_lat_droite_mob","o_lat_gauche_mob",
                "o_rot_droite_mob","o_rot_gauche_mob"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "tableau", "label": "Amplitudes lombaires", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        def _lf(k):
            v=lv(k,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None
        def mob_sel(label, key):
            stored=lv(key,"")
            idx=MOB_OPTS.index(stored) if stored in MOB_OPTS else 0
            chosen=st.selectbox(label,MOB_OPTS,index=idx,key=f"{key_prefix}_{key}")
            return "" if chosen=="— Non renseigné —" else chosen

        st.markdown('<div class="section-title">Mobilité lombaire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box"><small>1/3 = très limité · 2/3 = modérément limité · 3/3 = amplitude complète</small></div>',
                    unsafe_allow_html=True)
        mo1,mo2,mo3,mo4=st.columns(4)
        with mo1:
            schober=st.number_input("Schober modifié (cm)",0.0,30.0,_lf("o_schober"),0.5,
                                    key=f"{key_prefix}_schober",help="0 = non mesuré")
            flex_cm=st.number_input("Flexion doigt-sol (cm)",0.0,50.0,_lf("o_flexion_cm"),0.5,
                                    key=f"{key_prefix}_flex")
        with mo2:
            ext_mob=mob_sel("Extension","o_extension_mob")
        with mo3:
            lat_d=mob_sel("Latéroflexion Droite","o_lat_droite_mob")
            lat_g=mob_sel("Latéroflexion Gauche","o_lat_gauche_mob")
        with mo4:
            rot_d=mob_sel("Rotation Droite","o_rot_droite_mob")
            rot_g=mob_sel("Rotation Gauche","o_rot_gauche_mob")

        return {"o_schober":schober or "","o_flexion_cm":flex_cm or "",
                "o_extension_mob":ext_mob,"o_lat_droite_mob":lat_d,"o_lat_gauche_mob":lat_g,
                "o_rot_droite_mob":rot_d,"o_rot_gauche_mob":rot_g}

    @classmethod
    def is_filled(cls, bilan_data):
        v=str(bilan_data.get("o_schober","")).strip()
        try: return float(v)>0
        except: pass
        return any(bilan_data.get(k,"") not in ("","— Non renseigné —")
                   for k in ["o_extension_mob","o_lat_droite_mob"])

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        mob_keys=[("o_extension_mob","Extension"),("o_lat_droite_mob","Lat D"),
                  ("o_lat_gauche_mob","Lat G"),("o_rot_droite_mob","Rot D"),("o_rot_gauche_mob","Rot G")]
        colors=["#1a3c5e","#f57c00","#388e3c","#7b1fa2","#d32f2f"]
        fig=go.Figure()
        for (key,label),color in zip(mob_keys,colors):
            vals=[MOB_NUM.get(str(row.get(key,"")),None) for _,row in bilans_df.iterrows()]
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]
            yp=[v for v in vals if v is not None]
            txts=[str(row.get(key,"—")) or "—" for _,row in bilans_df.iterrows() if row.get(key,"")]
            if xp:
                fig.add_trace(go.Bar(name=label,x=xp,y=yp,marker_color=color,
                    text=txts,textposition="outside"))
        fig.update_layout(barmode="group",yaxis=dict(range=[0,4],tickvals=[1,2,3],
            ticktext=["1/3","2/3","3/3"],title="Amplitude"),
            height=350,plot_bgcolor="white",paper_bgcolor="white",
            legend=dict(orientation="h"))
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('mobilite_lombaire', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        schober_vals=[float(row.get("o_schober",0) or 0) for _,row in bilans_df.iterrows()]
        if any(v>0 for v in schober_vals):
            fig2=go.Figure()
            fig2.add_trace(go.Scatter(x=labels,y=schober_vals,mode="lines+markers+text",
                line=dict(color="#1a3c5e",width=2.5),marker=dict(size=9),
                text=[f"{v}cm" if v>0 else "" for v in schober_vals],textposition="top center"))
            fig2.add_hline(y=5,line_dash="dot",line_color="#388e3c",
                           annotation_text="5cm normal",annotation_position="right")
            fig2.update_layout(title="Schober modifié (cm)",yaxis_title="cm",
                               height=250,plot_bgcolor="white",paper_bgcolor="white")
            st.plotly_chart(fig2,use_container_width=True)
        table_rows = [
            {"label": "Schober (cm)", "col_key": "o_schober",
             "values": [r.get("o_schober","—") for _,r in bilans_df.iterrows()]},
            {"label": "Extension", "col_key": "o_extension_mob",
             "values": [r.get("o_extension_mob","—") for _,r in bilans_df.iterrows()]},
            {"label": "Lat D", "col_key": "o_lat_droite_mob",
             "values": [r.get("o_lat_droite_mob","—") for _,r in bilans_df.iterrows()]},
            {"label": "Lat G", "col_key": "o_lat_gauche_mob",
             "values": [r.get("o_lat_gauche_mob","—") for _,r in bilans_df.iterrows()]},
            {"label": "Rot D", "col_key": "o_rot_droite_mob",
             "values": [r.get("o_rot_droite_mob","—") for _,r in bilans_df.iterrows()]},
            {"label": "Rot G", "col_key": "o_rot_gauche_mob",
             "values": [r.get("o_rot_gauche_mob","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,"Schober (cm)":row.get("o_schober","—"),
                           "Extension":row.get("o_extension_mob","—"),
               "Lat D":row.get("o_lat_droite_mob","—"),"Lat G":row.get("o_lat_gauche_mob","—"),
               "Rot D":row.get("o_rot_droite_mob","—"),"Rot G":row.get("o_rot_gauche_mob","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Mobilité Rachis Lombaire", styles["section"]))
        story.append(Paragraph("Mesure des amplitudes rachidiennes lombaires et test de Schober.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        rows = [["Mouvement","Amplitude (°)","Distance doigt-sol (cm)","Observations"],
                ["Flexion","_____","_____",""],
                ["Extension","_____","",""],
                ["Latéroflexion D","_____","",""],
                ["Latéroflexion G","_____","",""],
                ["Rotation D","_____","",""],
                ["Rotation G","_____","",""]]
        t = Table(rows, colWidths=[4.5*cm,3.5*cm,4.5*cm,4.5*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        story.append(Paragraph("Test de Schober", styles["subsection"]))
        schober = Table([["Mesure initiale (S1→+10 cm) : _____ cm",
                          "Mesure en flexion : _____ cm",
                          "Différence : _____ cm (normal ≥ 5 cm)"]], colWidths=[5.5*cm,5.5*cm,6*cm])
        schober.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story.append(schober); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Notes : "+"_"*70, styles["normal"]))

