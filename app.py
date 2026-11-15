import streamlit as st
import google.generativeai as genai
import pandas as pd

# تنظیمات صفحه با طراحی مدرن
st.set_page_config(page_title="داشبورد حرفه‌ای تولید محتوا", layout="wide", page_icon="🚀")

# سایدبار حرفه‌ای (مشابه پیشنهاد ۲)
st.sidebar.title("🚀 منوی مدیریت")
menu = st.sidebar.radio("بخش‌ها", ["🏠 خانه و نمای کلی", "📌 اخبار داغ هفته", "💡 موضوعات دیپ‌دایو", "📊 آمار و تحلیل", "⚙️ تنظیمات"])

st.sidebar.markdown("---")
api_key = st.sidebar.text_input("کلید جمنای (Gemini API Key)", type="password")

model = None
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# بخش خانه و نمای کلی
if menu == "🏠 خانه و نمای کلی":
    st.title("🚀 داشبورد پیشرفته تولید محتوای تکنولوژی")
    st.markdown("مدیریت هوشمند جریان کاری، اخبار هفتگی و بخش دوم (دیپ‌دایو)")
    
    # کارت‌های آماری کلیدی
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="محتوا در صف", value="10", delta="+2")
    with col2:
        st.metric(label="تأیید شده", value="3", delta="1")
    with col3:
        st.metric(label="رد شده", value="2", delta="-1")
    with col4:
        st.metric(label="بازدید کل", value="12,424", delta="15%")
        
    st.markdown("---")
    st.subheader("🔄 جریان کاری تأیید محتوا")
    st.info("💡 برای بررسی و تایید اخبار یا موضوعات، از منوی سمت چپ به بخش‌های مربوطه مراجعه کنید.")

# بخش اخبار داغ هفته
elif menu == "📌 اخبار داغ هفته":
    st.subheader("📌 بخش اول: اخبار داغ و وایرال هفته")
    
    if "news_list" not in st.session_state:
        st.session_state.news_list = [
            {"title": "ربات‌های انسان‌نما با یادگیری شهودی", "status": "Pending", "desc": "قابلیت یادگیری کارهای خانه با مشاهده رفتار انسان."},
            {"title": "سیگنال‌های مرموز فضایی", "desc": "کشف امواج رادیویی ناشناخته از لبه منظومه شمسی.", "status": "Pending"},
            {"title": "بافت‌های زیستی چاپ‌شده سه‌بعدی", "desc": "ترمیم خودکار آسیب‌های بافتی داخل بدن.", "status": "Pending"}
        ]

    for idx, news in enumerate(st.session_state.news_list):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                status_icon = "🟢" if news["status"] == "Approved" else ("🔴" if news["status"] == "Rejected" else "⚪")
                st.markdown(f"### {status_icon} {news['title']}")
                st.write(f"_{news['desc']}_")
            with col2:
                if st.button("➕ تایید", key=f"app_{idx}"):
                    st.session_state.news_list[idx]["status"] = "Approved"
                    st.rerun()
            with col3:
                if st.button("❌ رد", key=f"rej_{idx}"):
                    st.session_state.news_list[idx]["status"] = "Rejected"
                    st.rerun()
            with col4:
                if st.button("🔍 بررسی هوشمند", key=f"rev_{idx}"):
                    if not model:
                        st.error("لطفاً کلید Gemini را در سایدبار وارد کنید!")
                    else:
                        with st.spinner("در حال استخراج منابع و متن..."):
                            detail_prompt = f"Write a simple sixth-grader level explanation and source links for: {news['title']}"
                            detail_res = model.generate_content(detail_prompt)
                            st.info(detail_res.text)
        st.divider()

# بخش موضوعات دیپ‌دایو
elif menu == "💡 موضوعات دیپ‌دایو":
    st.subheader("💡 بخش دوم: موضوعات عمیق و مینی‌داکیومنتری")
    if "deep_topics" not in st.session_state:
        st.session_state.deep_topics = [
            {"title": "رازهای پنهان الگوریتم‌های کلود شانون", "status": "Pending"},
            {"title": "تکنولوژی فراموش‌شده باتری‌های حالت جامد", "status": "Pending"},
            {"title": "پشت پرده پروژه‌های محرمانه فضایی مهار انرژی خورشیدی", "status": "Pending"}
        ]

    for idx, topic in enumerate(st.session_state.deep_topics):
        col1, col2 = st.columns([4, 1])
        with col1:
            t_icon = "✅" if topic["status"] == "Approved" else "📌"
            st.markdown(f"**{t_icon} {topic['title']}**")
        with col2:
            if st.button("تایید و سناریو", key=f"top_{idx}"):
                st.session_state.deep_topics[idx]["status"] = "Approved"
                if not model:
                    st.error("لطفاً کلید Gemini را وارد کنید.")
                else:
                    with st.spinner("آماده‌سازی محتوا و زوایای روایت..."):
                        content_prompt = f"Provide detailed background information, facts, and potential storytelling angles for: {topic['title']}"
                        content_res = model.generate_content(content_prompt)
                        st.success("موضوع تایید شد!")
                        st.write(content_res.text)
        st.divider()

# بخش آمار و تحلیل
elif menu == "📊 آمار و تحلیل":
    st.subheader("📊 آمارهای کلیدی تولید محتوا و تعاملات")
    chart_data = pd.DataFrame([120, 250, 180, 300, 450, 380, 520], columns=["بازدید ویدیوها"])
    st.line_chart(chart_data)
    st.metric(label="مجموع تعاملات کانال", value="12,424", delta="12%")

# بخش تنظیمات
elif menu == "⚙️ تنظیمات":
    st.subheader("⚙️ تنظیمات پیشرفته داشبورد")
    st.text_input("نام کانال یوتیوب", value="Tech & Conspiracy Channel")
    st.selectbox("وضعیت بروزرسانی خودکار", ["فعال", "غیرفعال"])
    st.success("همه سیستم‌ها پایدار و متصل هستند.")
