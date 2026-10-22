"""Local Streamlit review UI; launch with the documented loopback-only command."""
from pathlib import Path

import streamlit as st

from lung_nodule.contracts import Caliper, Decision, Review, digest
from lung_nodule.workspace import complete_review, load_workspace, overlay_slice, reviewed_report


def main():
    st.set_page_config(page_title="Local lung nodule research assistant", layout="wide")
    st.title("Lung nodule research assistant")
    st.warning("Research only. Candidates can be missed or incorrect. Scores are not cancer probabilities. Review the source CT.")
    st.caption("Local workspace review; run detection with the CLI first. This UI does not verify professional credentials or provide network authentication.")
    workspace = st.text_input("Workspace directory", "artifacts/lung-demo/workspace")
    try:
        study, hu = load_workspace(workspace)
    except (OSError, ValueError, KeyError) as exc:
        st.info(f"Open a valid workspace. {type(exc).__name__}: {exc}")
        return
    if study.model.synthetic_fixture:
        st.error("SYNTHETIC FIXTURE FINDER — not a trained lung nodule model. Use the pretrained detect command for model inference.")
    st.write(f"Study {study.study_id} | {study.input_kind} | {len(study.candidates)} candidates | {study.model.execution_device}")
    st.caption(f"Snapshot {digest(study)}. Source slices are zero-based; patient left/right labels are not inferred.")
    options = {c.candidate_id: c for c in study.candidates}
    chosen = st.selectbox("Jump to candidate", ["All slices", *options])
    if chosen in options:
        c = options[chosen]
        center = int(round((c.box_zyx[0]+c.box_zyx[3])/2))
    else:
        center = len(hu)//2
    z = st.slider("Source slice", 0, len(hu)-1, center, key=f"slice-{digest(study)}-{chosen}")
    left, right = st.columns(2)
    left.image(overlay_slice(study, hu, z, annotated=False), caption=f"Source slice {z}", width="stretch")
    right.image(overlay_slice(study, hu, z), caption="Detector boxes (amber); display is source axial geometry", width="stretch")
    st.code(f"Source slice {z} SHA-256: {study.sources[z].sha256}")
    st.dataframe([{"ID": c.candidate_id, "score (not malignancy)": c.score,
                   "box z0,y0,x0,z1,y1,x1": str(tuple(round(v,2) for v in c.box_zyx))} for c in study.candidates])
    with st.form(f"review-{digest(study)}"):
        decisions = []
        for c in study.candidates:
            st.write(c.candidate_id)
            status = st.selectbox(f"Decision {c.candidate_id}", ["uncertain", "accept", "reject"])
            caliper = None
            if st.checkbox(f"Record an in-plane caliper for {c.candidate_id}"):
                cols = st.columns(5)
                plane = cols[0].number_input(f"Slice {c.candidate_id}", min_value=0, max_value=len(hu)-1, value=int((c.box_zyx[0]+c.box_zyx[3])/2))
                y0 = cols[1].number_input(f"Start row {c.candidate_id}", min_value=0., max_value=float(hu.shape[1]-1), value=float(c.box_zyx[1]))
                x0 = cols[2].number_input(f"Start column {c.candidate_id}", min_value=0., max_value=float(hu.shape[2]-1), value=float(c.box_zyx[2]))
                y1 = cols[3].number_input(f"End row {c.candidate_id}", min_value=0., max_value=float(hu.shape[1]-1), value=float(c.box_zyx[1]))
                x1 = cols[4].number_input(f"End column {c.candidate_id}", min_value=0., max_value=float(hu.shape[2]-1), value=float(c.box_zyx[5]))
                caliper = Caliper(start_zyx=(plane,y0,x0), end_zyx=(plane,y1,x1))
            decisions.append(Decision(candidate_id=c.candidate_id, decision=status, caliper=caliper))
        reviewer = st.text_input("Reviewer name or local identifier")
        qualified = st.checkbox("I attest that I am qualified to review these research image findings and measurements")
        approved = st.checkbox("I reviewed the source images, every candidate and any caliper; approve this research summary")
        preview = st.form_submit_button("Preview measurements")
        submitted = st.form_submit_button("Complete research review")
    if preview:
        try:
            for d in decisions:
                if d.caliper:
                    plane = int(d.caliper.start_zyx[0])
                    st.image(overlay_slice(study,hu,plane,calipers=[d.caliper]),
                             caption=f"Preview {d.candidate_id}: {d.caliper.length_mm(study.geometry):.2f} mm; source slice {plane}")
        except ValueError as exc:
            st.error(str(exc))
    if submitted:
        try:
            review = Review(study_digest=digest(study), reviewer=reviewer,
                            qualified_reviewer_attestation=qualified, approved=approved, decisions=decisions)
            complete_review(workspace, review)
            st.success("Research review recorded; report available below.")
        except (ValueError, OSError) as exc:
            st.error(str(exc))
    if (Path(workspace) / "review.json").exists():
        try:
            report = reviewed_report(workspace)
            saved = Review.model_validate_json((Path(workspace) / "review.json").read_bytes())
            for d in saved.decisions:
                if d.caliper:
                    st.image(overlay_slice(study,hu,int(d.caliper.start_zyx[0]),calipers=[d.caliper]),
                             caption=f"Saved reviewed caliper {d.candidate_id}: {d.caliper.length_mm(study.geometry):.2f} mm")
            st.text(report)
            st.download_button("Download reviewed research summary", report, "lung-research-summary.md", "text/markdown")
        except (OSError, ValueError, KeyError) as exc:
            st.error(f"Report blocked: {exc}")


if __name__ == "__main__":
    main()
