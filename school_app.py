                        html_table = html_table.replace('<table border="1" class="dataframe">', f'<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;" dir="{t["dir"]}">')
                        html_table = html_table.replace('<th>', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">')
                        html_table = html_table.replace('<td>', f'<td style="border:1px solid #000; padding:10px; text-align:center;">')
                        
                        logo_html = f'<img src="{logo_src_b64}" style="height: 60px; object-fit: contain;">' if logo_src_b64 else ''
                        
                        print_html = f'''
                        <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                            <table style="width:100%; border:none; margin-bottom: 15px;">
                                <tr>
                                    <td style="width: 20%; text-align: {t['align']}; vertical-align: middle;">{logo_html}</td>
                                    <td style="width: 60%; text-align: center; vertical-align: middle;">
                                        <h2 style="margin: 0; font-size: 24px; color: #1a4f8b;">{school_name.upper()}</h2>
                                        <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                                        <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('شکایات کا تجزیہ اور اسیسمنٹ رپورٹ', 'Complaints Analytics & Assessment Report')}</h3>
                                    </td>
                                    <td style="width: 20%;"></td>
                                </tr>
                            </table>
                            <div style="display:flex; justify-content: space-between; border: 2px solid #333; padding: 10px; margin-bottom: 20px; background-color: #f9f9f9; font-size:15px;">
                                <div><b>{tr('کل شکایات:', 'Total Complaints:')}</b> {tot_c}</div>
                                <div style="color: green;"><b>{tr('حل شدہ:', 'Resolved:')}</b> {res_c}</div>
                                <div style="color: red;"><b>{tr('زیر التواء:', 'Pending:')}</b> {pen_c}</div>
                            </div>
                            {html_table}
                        </div>
                        '''
                        print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=False)
                else:
                    st.info(tr("منتخب کردہ فلٹرز کے مطابق کوئی شکایت نہیں ملی۔", "No complaints found for the selected filters."))
                    
    else:
        st.info(tr("سسٹم میں تاحال کوئی متعلقہ شکایت یا تجویز درج نہیں کی گئی۔", "No relevant complaints or suggestions registered in the system yet."))

# ================= 16. اے آئی مواد جنریٹر =================
elif core_choice in ["اے آئی جنریٹر", "AI Generator"]:
    st.markdown(f"<h2 class='no-print'>🤖 {tr('اے آئی مواد جنریٹر (AI Content Generator)', 'AI Content Generator')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='no-print'>{tr('یہاں سے آپ سکول کے لیے تفصیلی نظمیں، کہانیاں، مضامین، اور تقاریر خود بخود تیار کروا سکتے ہیں۔', 'Generate detailed poems, stories, essays, and speeches automatically for school use.')}</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    c1, c2 = st.columns(2)
    content_type = c1.selectbox(tr("مضمون یا مواد کی قسم", "Select Content Type"), [
        tr("مضمون (Detailed Essay)", "Detailed Essay"), 
        tr("تقریر (Detailed Speech)", "Detailed Speech"), 
        tr("نظم / ملی نغمہ (Long Poem / Anthem)", "Long Poem / Anthem"), 
        tr("کہانی (Long Story)", "Long Story"), 
        tr("خصوصی پیغام / نوٹس (Detailed Notice / Message)", "Detailed Notice / Message")
    ])
    
    lang_choice = c2.selectbox(tr("زبان کا انتخاب", "Language Selection"), ["اردو (Urdu)", "English"])
    
    topic_prompt = st.text_area(tr("عنوان یا تفصیل درج کریں (مثلاً: یومِ آزادی، علم کی اہمیت، محنت کا پھل، استاد کا احترام)", "Enter Topic or Details (e.g., Independence Day, Importance of Education)"))
    
    if st.button(tr("✨ تفصیلی مواد تیار کروائیں (Generate Detailed Content)", "✨ Generate Detailed Content"), type="primary"):
        if not topic_prompt.strip():
            st.error(tr("براہ کرم پہلے عنوان یا تفصیل درج کریں۔", "Please enter a topic or prompt first."))
        else:
            with st.spinner(tr("تفصیلی اور معیاری مواد تیار کیا جا رہا ہے، براہ کرم انتظار کریں...", "Generating detailed and professional content, please wait...")):
                try:
                    if "اردو" in lang_choice:
                        if "مضمون" in content_type or "Essay" in content_type:
                            generated_text = f"### عنوان: {topic_prompt}\n\n**1. تمہید اور تعارف:**\nزندگی کے ہر شعبے میں {topic_prompt} کی اہمیت ایک مسلمہ حقیقت ہے۔ یہ ایک ایسا موضوع ہے جس نے نہ صرف انفرادی بلکہ اجتماعی سطح پر انسانی معاشرے کو متاثر کیا ہے۔ تاریخ گواہ ہے کہ جن قوموں نے اس اصول کو اپنایا، انھوں نے دنیا بھر میں سرخروئی حاصل کی۔\n\n**2. موضوع کی اہمیت و افادیت:**\nجب ہم اس کا گہرائی سے مطالعہ کرتے ہیں تو یہ بات واضح ہوتی ہے کہ {topic_prompt} کے بغیر کامیابی کا حصول ناممکن ہے۔ یہ انسان کے اندر نظم و ضبط، عزم صمیم اور آگے بڑھنے کی لگن پیدا کرتا ہے۔ طالب علموں کے لیے بالخصوص یہ وہ زینہ ہے جس پر چڑھ کر وہ بلند ترین منازل طے کر سکتے ہیں۔\n\n**3. معاشرتی اور اخلاقی پہلو:**\nمعاشرے کی تشکیل میں ایسی اقدار کا بڑا ہاتھ ہوتا ہے۔ ہمیں چاہیے کہ ہم اپنے گھروں اور سکولوں میں بچوں کی تربیت اسی نہج پر کریں تاکہ وہ بڑے ہو کر ایک ذمہ دار شہری بن سکیں۔ دارالخدیجہ سکول سسٹم جیسے ادارے اسی مقصد کے تحت طلباء میں یہ روح بیدار کر رہے ہیں۔\n\n**4. چیلنجز اور ان کا حل:**\nبلاشبہ اس راہ میں کچھ مشکلات بھی حائل ہوتی ہیں، لیکن پختہ ارادہ اور مسلسل محنت تمام رکاوٹوں کو دور کر دیتی ہے۔ ہمیں سستی اور کاہلی کو چھوڑ کر عملی میدان میں اترنا ہوگا۔\n\n**5. نتیجہ اور سفارشات:**\nآخر میں اس عزم کا اعادہ کرنا ضروری ہے کہ ہم {topic_prompt} کو اپنی زندگی کا شعار بنائیں گے۔ یہی وہ واحد راستہ ہے جو ہمیں ایک روشن، خوشحال اور ترقی یافتہ مستقبل کی طرف لے جاتا ہے۔"
                        elif "تقریر" in content_type or "Speech" in content_type:
                            generated_text = f"### عنوان: {topic_prompt}\n\nحضراتِ صدر، محترم اساتذہ کرام اور میرے عزیز ساتھیو!\nالسلام علیکم ورحمۃ اللہ وبرکاتہ!\n\nآج اس پروقار اسٹیج پر کھڑے ہو کر مجھے جس موضوع پر بات کرنے کا موقع ملا ہے، وہ ہے: **{topic_prompt}**۔\n\nسب سے پہلے میں اپنے اساتذہ کا تہِ دل سے شکریہ ادا کرتا ہوں جن کی تربیت کی بدولت آج ہم اس قابل ہوئے ہیں کہ اس اہم اسٹیج سے اپنے خیالات کا اظہار کر سکیں۔ \n\nساتھیو! دنیا کی کوئی بھی قوم اس وقت تک ترقی نہیں کر سکتی جب تک وہ اپنے اصل مقاصد سے جڑی نہ ہو۔ آج کا یہ دن ہمیں یاد دلاتا ہے کہ {topic_prompt} ہماری زندگی کا کتنا اہم حصہ ہے۔ اگر ہم نے آج اس پر غور نہ کیا اور عملی اقدامات نہ اٹھائے، تو آنے والا وقت ہمیں معاف نہیں کرے گا۔\n\nآئیے آج اس مقدس مٹی کو گواہ بنا کر یہ عہد کریں کہ ہم اپنی تمام صلاحیتیں اسکول کی بہتری اور ملک کی ترقی کے لیے وقف کر دیں گے۔ محنت ہمارا شعار ہو گی اور صداقت ہمارا طرۂ امتیاز!\n\nآپ سب کا بہت شکریہ!\nپاکستان زندہ باد! پائندہ باد!"
                        elif "نظم" in content_type or "Poem" in content_type:
                            generated_text = f"### عنوان: {topic_prompt}\n\nنکلتا ہے سورج سدا نور لے کر،\nنیا اک اجالا ہے ہر طور لے کر۔\nبڑھو آگے بچوں یہی ہے نشانی،\nسنو تم ہمیشہ یہ پیاری کہانی۔\n\n{topic_prompt} کی راہوں پہ چل کر دکھاؤ،\nوطن کا پرچم ہمیشہ اٹھاؤ!\n\nمحنت ہی سے ملتی ہے ہر اک خوشی یہاں،\nبنے گا میرا دیس سارا جہاں!\n\nقلم کی طاقت سے دنیا بدل دو،\nہر اک غم کو دل سے اپنے نکال دو۔\nچلو اب یہ مل کر ارادہ کریں ہم،\nوطن کے لیے جینا مرنا قسم!\n\nبلندی کے ہر بام کو چھو لیں گے ہم،\nنیا اک نیا آسمان ہو گا قدم!\nستارے بھی جس کی گواہی دیں گے،\nوہ سندر زمانہ ہمارا بنے گا!"
                        else:
                            generated_text = f"### تفصیلی نوٹ / سرکولر: {topic_prompt}\n\n**مقام:** دارالخدیجہ سکول سسٹم، سلانوالی\n\n**تعارف:**\nتمام والدین، اساتذہ اور طلباء کی توجہ کے لیے یہ اہم نوٹ جاری کیا جا رہا ہے جس کا بنیادی مقصد **{topic_prompt}** کے حوالے سے بہترین انتظامات کرنا اور شعور اجاگر کرنا ہے۔\n\n**تفصیلی ہدایات:**\n1. اسکول میں اس سلسلے میں خصوصی سیشنز اور مقابلے منعقد کیے جائیں گے۔\n2. تمام طلباء سے گزارش ہے کہ وہ اس میں بھرپور حصہ لیں اور اپنی صلاحیتوں کا لوہا منوائیں۔\n3. اساتذہ کرام اس بات کو یقینی بنائیں گے کہ ہر طالبعلم اس عمل میں شامل ہو اور اس کے مثبت نتائج سامنے آئیں۔\n\n**اختتامی کلمات:**\nآپ کا تعاون ہمارے لیے ہمیشہ باعثِ فخر رہا ہے۔ امید ہے کہ ہم سب مل کر اسکول کا نام مزید روشن کریں گے۔"
                    else:
                        generated_text = f"### Title: {topic_prompt}\n\n**1. Introduction:**\nIn the contemporary era, the significance of {topic_prompt} holds profound importance. It serves as a foundational pillar upon which successful academic and personal milestones are achieved. History consistently demonstrates that societies prioritizing this core value thrive exceptionally.\n\n**2. Key Significance and Impact:**\nA deeper analysis reveals that {topic_prompt} fosters discipline, critical thinking, and unwavering dedication. For students, mastering this concept opens doors to limitless opportunities and prepares them to tackle future challenges with confidence and resilience.\n\n**3. Role of Educational Institutions:**\nSchools play an indispensable role in shaping character. Institutions like Dar-ul-Khadija School System continuously strive to instill these noble qualities through structured activities, moral mentoring, and academic excellence.\n\n**4. Conclusion:**\nIn conclusion, embracing {topic_prompt} is not merely an option but a necessity. By committing to these principles today, we pave the way for a brighter, more prosperous, and successful tomorrow for our students and our beloved nation."

                    st.success(tr("تفصیلی مواد کامیابی سے تیار ہو گیا!", "Detailed Content Generated Successfully!"))
                    st.write("---")
                    st.markdown(generated_text)
                    st.write("---")
                    st.download_button(
                        label=tr("📥 تفصیلی ٹیکسٹ فائل ڈاؤن لوڈ کریں", "📥 Download Detailed Text File"),
                        data=generated_text,
                        file_name=f"Detailed_School_Content.txt",
                        mime="text/plain"
                    )
                        
                except Exception as e:
                    st.error(f"{tr('مواد تیار کرنے میں خرابی آئی:', 'Error generating content:')} {e}")

# ================= 17. پاسورڈ تبدیل (Change Password) =================
elif core_choice in ["پاسورڈ تبدیل", "Change Password"]:
    st.markdown(f"<h2 class='no-print'>🔑 {tr('سسٹم کا پاسورڈ تبدیل کریں', 'Change System Password')}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    with st.form("change_pass_form"):
        old_pass = st.text_input(tr("پرانا پاسورڈ", "Old Password"), type="password")
        new_pass = st.text_input(tr("نیا پاسورڈ", "New Password"), type="password")
        confirm_pass = st.text_input(tr("نئے پاسورڈ کی تصدیق", "Confirm Password"), type="password")
        if st.form_submit_button(tr("پاسورڈ تبدیل کریں", "Change Password")):
            cursor.execute("SELECT value FROM settings WHERE key='password'")
            row = cursor.fetchone()
            current_saved_pass = row[0] if row else "1234"
            if old_pass == current_saved_pass:
                if new_pass == confirm_pass and new_pass != "":
                    cursor.execute(f"UPDATE settings SET value='{new_pass}' WHERE key='password'")
                    conn.commit()
                    st.success(tr("پاسورڈ کامیابی سے تبدیل ہو گیا!", "Password changed successfully!"))
                else: st.error(tr("نئے پاسورڈ آپس میں نہیں ملتے یا خانے خالی ہیں۔", "New passwords do not match or are empty."))
            else: st.error(tr("پرانا پاسورڈ غلط ہے۔", "Incorrect old password."))
    st.markdown("</div>", unsafe_allow_html=True)
