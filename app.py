import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="داشبورد مدیریت محتوای تکنولوژی", layout="wide", page_icon="🚀")

st.title("🚀 داشبورد شخصی تولید محتوای تکنولوژی")
st.markdown("مدیریت هوشمند اخبار هفتگی و بخش دوم (دیپ‌دایو)")

# Sidebar for API Key
st.sidebar.header("⚙️ تنظیمات")
api_key = st.sidebar.text_input("کلید جمنای (Gemini API Key)", type="password")

if not api_key:
    st.warning("لطفاً کلید Gemini API که در مرحله اول ساختید را در منوی سمت چپ وارد کنید تا سیستم فعال شود.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

tab1, tab2 = st.tabs(["📌 بخش اول: اخبار داغ هفته", "💡 بخش دوم: موضوعات دیپ‌دایو"])

with tab1:
    st.subheader("لیست اخبار داغ و وایرال هفته")
    
    if "news_list" not in st.session_state:
        st.session_state.news_list = [
            {"title": "ربات‌های انسان‌نما با یادگیری شهودی", "status": "Pending", "desc": "قابلیت یادگیری کارهای خانه با مشاهده رفتار انسان."},
            {"title": "سیگنال‌های مرموز فضایی", "desc": "کشف امواج رادیویی ناشناخته از لبه منظومه شمسی.", "status": "Pending"},
            {"title": "بافت‌های زیستی چاپ‌شده سه‌بعدی", "desc": "ترمیم خودکار آسیب‌های بافتی داخل بدن.", "status": "Pending"}
        ]

    for idx, news in enumerate(st.session_state.news_list):
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            status_icon = "🟢" if news["status"] == "Approved" else ("🔴" if news["status"] == "Rejected" else "⚪")
            st.markdown(f"{status_icon} **{news['title']}**\n\n_{news['desc']}_")
        with cols[1]:
            if st.button("➕ تایید", key=f"app_{idx}"):
                st.session_state.news_list[idx]["status"] = "Approved"
                st.rerun()
        with cols[2]:
            if st.button("❌ رد", key=f"rej_{idx}"):
                st.session_state.news_list[idx]["status"] = "Rejected"
                st.rerun()
        with cols[3]:
            if st.button("🔍 بررسی", key=f"rev_{idx}"):
                with st.spinner("در حال استخراج منابع و متن ساده..."):
                    detail_prompt = f"Write a simple sixth-grader level explanation and source links for: {news['title']}"
                    detail_res = model.generate_content(detail_prompt)
                    st.info(detail_res.text)

with tab2:
    st.subheader("بخش دوم: موضوعات تاثیرگذار و دیپ‌دایو")
    if "deep_topics" not in st.session_state:
        st.session_state.deep_topics = [
            {"title": "رازهای پنهان الگوریتم‌های کلود شانون و تاثیر آن بر دنیای دیجیتال امروز", "status": "Pending"},
            {"title": "تکنولوژی فراموش‌شده‌ای که ساخت باتری‌های حالت جامد را متحول کرد", "status": "Pending"},
            {"title": "پشت پرده‌ی پروژه‌های محرمانه فضایی برای مهار انرژی خورشیدی در مدار", "status": "Pending"}
        ]

    for idx, topic in enumerate(st.session_state.deep_topics):
        cols = st.columns([4, 1])
        with cols[0]:
            t_icon = "✅" if topic["status"] == "Approved" else "📌"
            st.markdown(f"{t_icon} **{topic['title']}**")
        with cols[1]:
            if st.button("انتخاب و بررسی", key=f"top_{idx}"):
                st.session_state.deep_topics[idx]["status"] = "Approved"
                with st.spinner("آماده‌سازی محتوا، اطلاعات و منابع..."):
                    content_prompt = f"Provide detailed background information, facts, and potential storytelling angles for: {topic['title']}"
                    content_res = model.generate_content(content_prompt)
                    st.success("موضوع تایید شد!")
                    st.write(content_res.text)
