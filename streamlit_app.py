"""Landing page for the AI solutions guide, for Streamlit Community Cloud.

The first page offers Arabic or English. Choosing one opens that flipbook, which is
read from docs/ar or docs/en, so the books are kept in one place only.
Run it locally with: streamlit run streamlit_app.py
"""
import base64
import mimetypes
import re
from pathlib import Path

import streamlit as st

SITE = Path(__file__).parent / "docs"
LANGUAGES = ("ar", "en")
SPHERE = SITE / "ar" / "assets" / "sphere-soft.png"
EMAIL = "44hala2003@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/hala-al-attiyat-062514220"

BASE_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
  :root {
    --red-hi: #D0080F;
    --red-lo: #8E0107;
    --blue: #2F6FA8;
    --sky: #9CC3EA;
    --sky-1: #DCE8F6;
    --sky-2: #F4F8FD;
    --ink: #14213A;
    --muted: #41506B;
    --latin: Poppins, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    --naskh: 'Noto Naskh Arabic', 'Traditional Arabic', 'Geeza Pro', serif;
  }
  header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
  .stApp { background: radial-gradient(ellipse at 50% 30%, var(--sky-2) 0%, var(--sky-1) 58%, #BFD3E9 100%) fixed; }
</style>
"""

# Layout idea: one open book. Its right page is Arabic and its left page is English.
LANDING_CSS = """
<style>
  .stMainBlockContainer { display: flex; flex-direction: column; justify-content: center; max-width: 1020px; min-height: 100vh; min-height: 100dvh; padding: 16px 20px 64px; }
  .st-key-sphere { position: relative; z-index: 2; margin-bottom: -40px; pointer-events: none; }
  .st-key-sphere [data-testid="stImage"], .st-key-sphere [data-testid="stImageContainer"] { display: flex; justify-content: center; width: 100%; }
  .st-key-sphere img { width: 196px !important; }

  .st-key-book [data-testid="stHorizontalBlock"] { flex-direction: row-reverse; gap: 0; border-radius: 20px; box-shadow: 4px 0 0 #FFFFFF, 5px 0 0 #C3D4E7, -4px 0 0 #FFFFFF, -5px 0 0 #C3D4E7, 0 22px 46px rgba(20, 33, 58, .22); }
  .st-key-book [data-testid="stColumn"] { position: relative; display: flex; background: #FFFFFF; }
  .st-key-book [data-testid="stColumn"] > [data-testid="stVerticalBlock"], .st-key-book [data-testid="stColumn"] [data-testid="stLayoutWrapper"] { flex: 1; }
  .st-key-book [data-testid="stColumn"]::before { content: ""; position: absolute; top: 0; bottom: 0; width: 44px; pointer-events: none; }
  .st-key-book [data-testid="stColumn"]:first-child { border-radius: 0 20px 20px 0; }
  .st-key-book [data-testid="stColumn"]:first-child::before { left: 0; background: linear-gradient(90deg, rgba(20, 33, 58, .13), rgba(20, 33, 58, 0)); }
  .st-key-book [data-testid="stColumn"]:last-child { border-radius: 20px 0 0 20px; }
  .st-key-book [data-testid="stColumn"]:last-child::before { right: 0; background: linear-gradient(270deg, rgba(20, 33, 58, .13), rgba(20, 33, 58, 0)); }
  .st-key-leaf_ar, .st-key-leaf_en { display: flex; flex-direction: column; gap: 6px; padding: 42px 36px 34px; }
  .st-key-leaf_ar [data-testid="stElementContainer"]:has(.leaf), .st-key-leaf_en [data-testid="stElementContainer"]:has(.leaf) { width: 100%; }

  .leaf { display: flex; flex-direction: column; align-items: flex-start; gap: 14px; margin-bottom: 12px; }
  .leaf p, .leaf h2 { margin: 0; padding: 0; }
  .leaf .pill { padding: 3px 14px; border: 1px solid var(--sky); border-radius: 16px; background: #FFFFFF; color: var(--blue); font-weight: 600; }
  .leaf h2 { color: var(--ink); font-weight: 700; text-wrap: balance; }
  .leaf .line { color: var(--muted); text-wrap: pretty; }
  .leaf-ar { direction: rtl; font-family: var(--naskh); }
  .leaf-ar .pill { font-size: 16px; line-height: 24px; }
  .leaf-ar h2 { font-family: var(--naskh); font-size: 31px; line-height: 40px; }
  .leaf-ar .line { font-size: 20px; line-height: 34px; }
  .leaf-en { direction: ltr; font-family: var(--latin); }
  .leaf-en .pill { font-size: 13px; line-height: 20px; }
  .leaf-en h2 { font-family: var(--latin); font-size: 27px; line-height: 40px; letter-spacing: -0.5px; }
  .leaf-en .line { font-size: 16px; line-height: 27px; }

  .st-key-go_ar, .st-key-go_en { margin-top: auto; }
  .st-key-go_ar { align-self: flex-end; direction: rtl; }
  .st-key-go_ar button, .st-key-go_en button { min-height: 52px; padding: 10px 24px; border: 0; border-radius: 12px; background: linear-gradient(135deg, var(--red-hi) 0%, var(--red-lo) 100%); box-shadow: 0 8px 18px rgba(142, 1, 7, .28); color: #FFFFFF; }
  .st-key-go_ar button:hover, .st-key-go_en button:hover { color: #FFFFFF; filter: brightness(1.08); }
  .st-key-go_ar button:focus-visible, .st-key-go_en button:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; color: #FFFFFF; }
  .st-key-go_ar button p { font-family: var(--naskh); font-size: 21px; line-height: 30px; font-weight: 700; }
  .st-key-go_en button p { font-family: var(--latin); font-size: 16.5px; line-height: 28px; font-weight: 700; }

  .foot { position: fixed; left: 0; right: 0; bottom: 0; z-index: 5; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 6px 22px; padding: 12px 20px; background: linear-gradient(135deg, #1F3322 0%, #5B6A49 100%); color: #DDE8D8; font-family: var(--latin); font-size: 14px; line-height: 22px; }
  .foot b { color: #FFFFFF; font-weight: 600; }
  .foot a { color: #FFFFFF; }
  .foot .ar { font-family: var(--naskh); font-size: 16.5px; }

  @media (max-width: 720px) {
    .stMainBlockContainer { justify-content: flex-start; padding: 4px 16px 16px; }
    .st-key-sphere { margin-bottom: -18px; }
    .st-key-sphere img { width: 100px !important; }
    .st-key-book [data-testid="stHorizontalBlock"] { flex-direction: column; flex-wrap: nowrap; gap: 12px; border-radius: 0; box-shadow: none; }
    .st-key-book [data-testid="stColumn"], .st-key-book [data-testid="stColumn"]:first-child, .st-key-book [data-testid="stColumn"]:last-child { flex: 0 0 auto; width: 100%; min-width: 100%; border-radius: 18px; box-shadow: 0 10px 24px rgba(20, 33, 58, .16); }
    .st-key-book [data-testid="stColumn"]::before, .leaf .pill { display: none; }
    .st-key-leaf_ar, .st-key-leaf_en { padding: 16px 20px 18px; }
    .leaf { gap: 8px; margin-bottom: 6px; }
    .leaf-ar h2 { font-size: 26px; line-height: 36px; }
    .leaf-en h2 { font-size: 22px; line-height: 30px; }
    .leaf-ar .line { font-size: 18.5px; line-height: 29px; }
    .leaf-en .line { font-size: 15px; line-height: 24px; }
    .st-key-go_ar button, .st-key-go_en button { min-height: 46px; padding: 8px 20px; }
    .st-key-go_ar button p { font-size: 19.5px; }
    .st-key-go_en button p { font-size: 15.5px; }
    .foot { position: static; margin: 16px -16px -16px; }
  }
</style>
"""

# The book fills the whole window. The language button floats in the corner its readers start from.
BOOK_CSS = """
<style>
  html, body, .stApp, .stMain { overflow: hidden !important; }
  .stMainBlockContainer { padding: 0 !important; max-width: none !important; }
  iframe { position: fixed; inset: 0; z-index: 1; width: 100vw !important; height: 100vh !important; height: 100dvh !important; border: 0; }
  .st-key-back { position: fixed; top: 8px; z-index: 10; width: auto !important; }
  .st-key-back button { min-height: 34px; padding: 2px 14px; border: 1px solid var(--sky); border-radius: 10px; background: rgba(255, 255, 255, .92); color: var(--blue); }
  .st-key-back button:hover { border-color: var(--blue); color: var(--blue); }
  .st-key-back button p { font-size: 14px; line-height: 20px; font-weight: 600; }
</style>
"""


@st.cache_data(show_spinner=False)
def load_book(language, version):
    """Return one flipbook as a single HTML string, with its images built in.

    version is the file's modified time, so an edited book is not served from the cache.
    """
    folder = SITE / language
    html = (folder / "index.html").read_text(encoding="utf-8")

    def embed(match):
        image = folder / match.group(0)
        mime = mimetypes.guess_type(image.name)[0]
        return f"data:{mime};base64,{base64.b64encode(image.read_bytes()).decode('ascii')}"

    html = re.sub(r"assets/[\w.-]+", embed, html)
    # Inside an embedded frame the page has no address of its own, so Share must read the app's.
    return html.replace(
        "location.href.split('#')[0]",
        "(function () { try { return window.top.location.href; } catch (e) { return location.href; } })().split('#')[0]",
    )


def choose(language):
    st.query_params["lang"] = language


def back_to_landing():
    st.query_params.clear()


def show_landing():
    st.html(LANDING_CSS)
    with st.container(key="sphere", horizontal_alignment="center"):
        st.image(str(SPHERE), width=196)
    with st.container(key="book"):
        # The first column is drawn on the right on wide screens, and on top on phones.
        arabic, english = st.columns(2, gap=None)
        with arabic, st.container(key="leaf_ar"):
            st.html(
                '<div class="leaf leaf-ar" lang="ar" dir="rtl">'
                '<p class="pill">كتيّب مصوّر</p>'
                "<h2>حلول بالذكاء الاصطناعي لمنشآتكم</h2>"
                '<p class="line">كيف يمكن للذكاء الاصطناعي أن يساند فريقكم في الأعمال اليومية، بما يناسب احتياج منشأتكم وميزانيتها، دون الحاجة إلى قسم تقني.</p>'
                "</div>"
            )
            st.button("المتابعة بالعربية ←", key="go_ar", type="primary", on_click=choose, args=("ar",))
        with english, st.container(key="leaf_en"):
            st.html(
                '<div class="leaf leaf-en" lang="en" dir="ltr">'
                '<p class="pill">An illustrated guide</p>'
                "<h2>AI Solutions for Your Business</h2>"
                '<p class="line">How AI could support your team\'s daily work, shaped around your company\'s needs and budget, with no technical department required.</p>'
                "</div>"
            )
            st.button("Continue in English →", key="go_en", type="primary", on_click=choose, args=("en",))
    st.html(
        '<div class="foot">'
        '<span><b>Hala Al-Attiyat</b> | <b class="ar" lang="ar" dir="rtl">حلا العطيات</b></span>'
        f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
        f'<a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>'
        "</div>"
    )


def show_book(language):
    st.html(BOOK_CSS)
    side = "right" if language == "ar" else "left"
    font = "--naskh" if language == "ar" else "--latin"
    st.html(f"<style>.st-key-back {{ {side}: 12px; }} .st-key-back button p {{ font-family: var({font}); }}</style>")
    label = "تغيير اللغة" if language == "ar" else "Change language"
    st.button(label, key="back", on_click=back_to_landing)
    page = SITE / language / "index.html"
    st.iframe(load_book(language, page.stat().st_mtime), height=800)


st.set_page_config(
    page_title="حلول بالذكاء الاصطناعي لمنشآتكم | AI Solutions for Your Business",
    page_icon=str(SPHERE),
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.html(BASE_CSS)

# Only these two fixed values ever choose what is embedded; anything else shows the landing page.
selected = st.query_params.get("lang")
if selected in LANGUAGES:
    show_book(selected)
else:
    show_landing()
