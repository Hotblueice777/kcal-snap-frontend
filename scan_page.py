# scan_page.py

import os
import io, time, requests  # type: ignore
import streamlit as st  # type: ignore
from PIL import Image, ExifTags

def render(): 
    BACKEND = os.getenv("BACKEND_URL")
    
    st.markdown("""
        <h1 style='margin-bottom:0; color:#766A8F'>KcalSnap</h1>
        <p style='font-size:18px; color:#666666; margin-top:0'>
        Snap your meal, get instant calorie insights
        </p>
        """, unsafe_allow_html=True)

    # Correct photo orientation
    def fix_orientation(img: Image.Image) -> Image.Image:
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = dict(img._getexif().items()) if hasattr(img, "_getexif") and img._getexif() else {}  # type: ignore
            o = exif.get(orientation)
            if o == 3: img = img.rotate(180, expand=True)
            elif o == 6: img = img.rotate(270, expand=True)
            elif o == 8: img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img


    # Generate JPEG bytes
    def jpeg_bytes_from_uploader(uploaded):
        img = Image.open(uploaded).convert("RGB")
        img = fix_orientation(img)
        w, h = img.size
        max_side = max(w, h)
        if max_side > 512:
            scale = 512 / max_side
            img = img.resize((int(w * scale), int(h * scale)))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        buf.seek(0)
        return buf


    # Main interface
    with st.form("capture"):
        photo = st.camera_input(" ", label_visibility="collapsed") or st.file_uploader("…or choose from library", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
       
        # Display the image immediately after it is uploaded/captured
        if photo:
            # Use st.image to display the image. 
            # Streamlit handles the object type (UploadedFile) automatically.
            st.image(photo, caption=photo.name if hasattr(photo, 'name') else 'Captured Photo', use_column_width=True)
        # 🌟 END NEW CODE

        submitted = st.form_submit_button("Analyze")

        if submitted and photo:
            with st.spinner("Analyzing…"):
                t0 = time.time()
                buf = jpeg_bytes_from_uploader(photo)
                files = {"image": ("photo.jpg", buf, "image/jpeg")}
                r = requests.post(f"{BACKEND}/api/predict", files=files, timeout=15)
                r.raise_for_status()
                data = r.json()
                topk = data["topk"]

            st.subheader("Prediction")
            labels = [f'{item["label"]} ({item["score"]:.2f})' for item in topk]
            idx = st.radio("Top-3 candidates", list(range(len(labels))), format_func=lambda i: labels[i], horizontal=True, index=0)
            chosen = topk[idx]["label"]

            # Portion size slider
            default_grams = 180 if chosen not in ("pizza", "ramen", "fried_rice", "salad") else {
                "pizza": 150, "ramen": 450, "fried_rice": 250, "salad": 220
            }[chosen]
            grams = st.slider("Portion (grams)", 50, 800, value=default_grams, step=10)

            # Load ingredients and nutrition info only when a food item is selected
            if "chosen" in locals() and chosen not in (None, "", "unknown"):
                try:
                    # Request optional ingredients from backend
                    r = requests.get(f"{BACKEND}/api/addons", params={"label": chosen}, timeout=10)
                    r.raise_for_status()
                    addon_data = r.json()
                    addons_options = [(a["addon"], a["addon"]) for a in addon_data]
                except Exception as e:
                    st.warning(f"⚠️ Unable to load ingredient options: {e}")
                    addons_options = []

                # Ingredient selection
                picked = st.multiselect(
                    "Add / remove items",
                    addons_options,
                    format_func=lambda kv: kv[1],
                )

                # Request nutrition information
                addon_keys = ",".join(k for k, _ in picked)
                with st.spinner("Fetching nutrition…"):
                    r2 = requests.get(
                        f"{BACKEND}/api/nutrition",
                        params={"label": chosen, "grams": grams, "addons": addon_keys},
                        timeout=10,
                    )
                    r2.raise_for_status()
                    nutr = r2.json()

                # Display nutrition results
                st.subheader("Estimated nutrition")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Calories (kcal)", nutr["totals"]["kcal"], f'{nutr["range"]["kcal_low"]}–{nutr["range"]["kcal_high"]}')
                c2.metric("Protein (g)", nutr["totals"]["protein_g"])
                c3.metric("Fat (g)", nutr["totals"]["fat_g"])
                c4.metric("Carbs (g)", nutr["totals"]["carb_g"])
                st.caption(f"Source: {nutr['source']} · Estimate (not medical advice) · Cached: {nutr.get('cached', False)}")
                st.caption(f"End-to-end latency: {round((time.time()-t0)*1000)} ms")
                st.session_state["last_chosen"] = chosen
                st.session_state["last_nutr"] = nutr
            else:
                st.info("🧩 Wait for the image ready…")

    # Add to My Meals
    if st.button("➕ Add today's meal"):
        chosen = st.session_state.get("last_chosen")
        nutr = st.session_state.get("last_nutr")

        if not chosen or not nutr:
            st.warning("⚠️ Please analyze a photo first before adding a meal.")
        else:
            if "meals" not in st.session_state:
                st.session_state["meals"] = []

            new_meal = {
                "time": time.strftime("%H:%M"),
                "name": chosen,
                "cal": nutr["totals"]["kcal"],
                "protein": nutr["totals"]["protein_g"],
                "fat": nutr["totals"]["fat_g"],
                "carb": nutr["totals"]["carb_g"],
            }
            st.session_state["meals"].append(new_meal)
            st.success(f"✅ Added {chosen} ({nutr['totals']['kcal']} kcal) to today's meals!")