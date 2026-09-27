import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

# ==========================================
# 1. إعدادات الصفحة والواجهة الغامقة الفخمة (Deep Focus Dark Mode)
# ==========================================
st.set_page_config(page_title="نظام التركيز العميق - Deep Work", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* خلفية داكنة فخمة ومريحة للعين */
    .stApp { background-color: #0d1117 !important; color: #e6edf3 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* العناوين بلون ذهبي هادئ وتصميم احترافي */
    h1, h2, h3, h4 { color: #f0b429 !important; font-weight: 700 !important; }
    p, label, span, .stMarkdown { color: #c9d1d9 !important; }
    
    /* البطاقات والحواف لكل جزء (Cards with borders) */
    .deep-card {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    /* حقول الإدخال والقوائم بتصميم داكن متناسق */
    input, textarea, select, div[data-baseweb="select"] > div { 
        background-color: #0d1117 !important; 
        color: #e6edf3 !important; 
        border: 1px solid #30363d !important; 
        border-radius: 8px !important; 
    }
    
    /* الأزرار باحترافية */
    .stButton>button { 
        background-color: #238636 !important; 
        color: #ffffff !important; 
        border-radius: 8px !important; 
        border: none !important; 
        font-weight: bold !important; 
        padding: 10px 24px; 
    }
    .stButton>button:hover { background-color: #2ea043 !important; }
    
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #e6edf3 !important; }
    hr { border-color: #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. الاتصال بقاعدة البيانات
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
    st.stop()

# التحقق من الجلسة (نستخدم جدول المستخدمين المشترك أو تسجيل خفيف)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None

# شاشة دخول سريعة إن لم يكن مسجلاً
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 40px;'>🧠 Deep Work System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e;'>نظام الإنجاز العميق والتخطيط الواعي</p>", unsafe_allow_html=True)
        
        with st.form("quick_login"):
            m_input = st.text_input("رقم الموبايل")
            p_input = st.text_input("كلمة المرور", type="password")
            submitted = st.form_submit_button("دخول لنظام التركيز", use_container_width=True)
            
            if submitted:
                try:
                    res = supabase.table('istiqama_users').select('*').eq('mobile', m_input).execute()
                    if res.data:
                        user = res.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['id']
                        st.session_state.user_name = user['name']
                        st.rerun()
                    else:
                        st.error("المستخدم غير مسجل.")
                except Exception as ex:
                    st.error(f"خطأ: {ex}")
    st.stop()

user_id = st.session_state.user_id
user_name = st.session_state.user_name

# ==========================================
# 3. القائمة الجانبية للتنقل بين الأقسام
# ==========================================
with st.sidebar:
    st.markdown(f"### 🧠 أهلاً بك، {user_name}")
    st.markdown("---")
    app_mode = st.radio(
        "اختر القسم:",
        [
            "📚 إدارة المواد والمجالات", 
            "🗓️ التخطيط المسبق (خطة الغد والأيام)", 
            "⚡ تنفيذ وتقييم جلسات اليوم", 
            "📊 إحصائيات ومعدل الأداء"
        ]
    )
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# القسم الأول: إدارة المواد والمجالات الرئيسية
# ==========================================
if app_mode == "📚 إدارة المواد والمجالات":
    st.markdown("<h1>📚 إدارة المواد والمجالات الرئيسية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e;'>أنشئ موادك أو مجالات تركيزك (مثل: برمجة، قراءة كتب، تطوير لغات، إلخ) لربط جلساتك بها.</p>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### ➕ إضافة مجال جديد")
        with st.form("add_subject_form"):
            subj_name = st.text_input("اسم المادة أو المجال")
            subj_desc = st.text_area("وصف مختصر أو أهداف المجال")
            submit_subj = st.form_submit_button("حفظ المجال", use_container_width=True)
            
            if submit_subj:
                if subj_name:
                    try:
                        supabase.table('deep_subjects').insert({
                            'user_id': user_id,
                            'subject_name': subj_name,
                            'description': subj_desc
                        }).execute()
                        st.success(f"✅ تمت إضافة المجال '{subj_name}' بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى إدخال اسم المادة.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_b:
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### 📋 مجالاتك الحالية")
        try:
            subs_res = supabase.table('deep_subjects').select('*').eq('user_id', user_id).execute()
            if subs_res.data:
                df_subs = pd.DataFrame(subs_res.data)
                st.dataframe(df_subs[['subject_name', 'description']], use_container_width=True)
            else:
                st.info("لم تقم بإضافة أي مجالات بعد.")
        except Exception as e:
            st.error(f"خطأ في جلب المجالات: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الثاني: التخطيط المسبق (خطة الغد والأيام القادمة)
# ==========================================
elif app_mode == "🗓️ التخطيط المسبق (خطة الغد والأيام)":
    st.markdown("<h1>🗓️ التخطيط المسبق لجلسات التركيز</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e;'>خطط ليومك غداً بوعي: حدد المادة، الوقت بدقة، وما تتوقع إنجازه لتستيقظ على رؤية واضحة.</p>", unsafe_allow_html=True)
    
    try:
        subs_res = supabase.table('deep_subjects').select('id, subject_name').eq('user_id', user_id).execute()
        subjects_list = subs_res.data if subs_res.data else []
    except:
        subjects_list = []
        
    if not subjects_list:
        st.warning("⚠️ يجب عليك إضافة مجالات أو مواد أولاً من قسم 'إدارة المواد والمجالات'.")
    else:
        subj_dict = {s['subject_name']: s['id'] for s in subjects_list}
        
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        with st.form("plan_form"):
            col_p1, col_p2 = st.columns(2)
            plan_date = col_p1.date_input("تاريخ تنفيذ الجلسة", date.today() + timedelta(days=1))
            chosen_subj_name = col_p2.selectbox("اختر المادة / المجال", options=list(subj_dict.keys()))
            
            col_t1, col_t2 = st.columns(2)
            start_t = col_t1.time_input("وقت البدء")
            end_t = col_t2.time_input("وقت الانتهاء")
            
            expected_tasks = st.text_area("ماذا تتوقع أن تنجز في هذه الجلسة بالتفصيل؟")
            
            submit_plan = st.form_submit_button("📅 اعتماد وجدولة الجلسة", use_container_width=True)
            
            if submit_plan:
                if expected_tasks:
                    try:
                        supabase.table('deep_plans').insert({
                            'user_id': user_id,
                            'plan_date': str(plan_date),
                            'subject_id': subj_dict[chosen_subj_name],
                            'start_time': str(start_t),
                            'end_time': str(end_t),
                            'expected_tasks': expected_tasks,
                            'status': 'مخطط'
                        }).execute()
                        st.success("🎉 تم حفظ خطة الجلسة بنجاح!")
                    except Exception as e:
                        st.error(f"خطأ أثناء الحفظ: {e}")
                else:
                    st.warning("يرجى كتابة المهام المتوقعة.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # استعراض الخطط القادمة
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### 📋 جدول خططك القادمة")
        try:
            plans_res = supabase.table('deep_plans').select('id, plan_date, start_time, end_time, expected_tasks, status, deep_subjects(subject_name)').eq('user_id', user_id).gte('plan_date', str(date.today())).order('plan_date').execute()
            if plans_res.data:
                df_plans = pd.DataFrame(plans_res.data)
                st.dataframe(df_plans, use_container_width=True)
            else:
                st.info("لا توجد خطط مستقبلية مسجلة.")
        except Exception as e:
            st.error(f"خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الثالث: تنفيذ وتقييم جلسات اليوم
# ==========================================
elif app_mode == "⚡ تنفيذ وتقييم جلسات اليوم":
    st.markdown("<h1>⚡ تنفيذ وتقييم جلسات اليوم</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #8b949e;'>جلساتك المخططة لتاريخ اليوم: <b>{date.today()}</b>. سجل أداءك وتركيزك فور انتهائها.</p>", unsafe_allow_html=True)
    
    today_str = str(date.today())
    
    try:
        # جلب جلسات اليوم المخططة
        today_plans = supabase.table('deep_plans').select('id, start_time, end_time, expected_tasks, deep_subjects(subject_name)').eq('user_id', user_id).eq('plan_date', today_str).execute()
        plans = today_plans.data if today_plans.data else []
    except:
        plans = []
        
    if not plans:
        st.info("📌 لا توجد جلسات مخططة لهذا اليوم. يمكنك التخطيط مسبقاً من قسم 'التخطيط المسبق'.")
    else:
        for idx, plan in enumerate(plans):
            st.markdown(f'<div class="deep-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🎯 الجلسة #{idx+1}: {plan['deep_subjects']['subject_name']}")
            st.markdown(f"**الوقت المخطط:** من {plan['start_time']} إلى {plan['end_time']} | **المهام:** {plan['expected_tasks']}")
            
            # التحقق إذا كانت الجلسة مقيمة مسبقاً
            try:
                exec_res = supabase.table('deep_execution_logs').select('*').eq('plan_id', plan['id']).execute()
                exec_data = exec_res.data[0] if exec_res.data else None
            except:
                exec_data = None
                
            with st.form(f"exec_form_{plan['id']}"):
                completed = st.checkbox("✅ هل أتممت هذه الجلسة بنجاح؟", value=exec_data['completed'] if exec_data else False)
                
                focus_opts = ['تركيز عميق 100%', 'عالي', 'متوسط', 'مشتت / منخفض']
                f_idx = focus_opts.index(exec_data['focus_level']) if exec_data and exec_data['focus_level'] in focus_opts else 0
                focus_level = st.selectbox("🧠 ما هو مستوى تركيزك الفعلي؟", focus_opts, index=f_idx)
                
                actual_min = st.number_input("⏱️ كم دقيقة قضيتها فعلياً في التركيز؟", min_value=0, max_value=600, value=exec_data['actual_minutes'] if exec_data else 45)
                notes = st.text_area("📝 ملاحظات أو خواطر حول أداء الجلسة", value=exec_data['notes'] if exec_data else "")
                
                submit_exec = st.form_submit_button("💾 حفظ تقييم الجلسة", use_container_width=True)
                
                if submit_exec:
                    try:
                        payload = {
                            'user_id': user_id,
                            'plan_id': plan['id'],
                            'execution_date': today_str,
                            'completed': completed,
                            'focus_level': focus_level,
                            'actual_minutes': actual_min,
                            'notes': notes
                        }
                        
                        if exec_data:
                            supabase.table('deep_execution_logs').update(payload).eq('id', exec_data['id']).execute()
                            st.success("✅ تم تحديث تقييم الجلسة بنجاح!")
                        else:
                            supabase.table('deep_execution_logs').insert(payload).execute()
                            st.success("🎉 أحسنت! تم تسجيل إنجاز الجلسة وحفظ تقييمك.")
                    except Exception as ex:
                        st.error(f"خطأ أثناء الحفظ: {ex}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الرابع: إحصائيات ومعدل الأداء
# ==========================================
elif app_mode == "📊 إحصائيات ومعدل الأداء":
    st.markdown("<h1>📊 إحصائيات وتقارير معدل الأداء</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e;'>تأمل ساعات تركيزك العميق وتطور إنجازك بمرور الأيام عبر الرسوم البيانية الدقيقة.</p>", unsafe_allow_html=True)
    
    try:
        # جلب سجلات التنفيذ للمستخدم الحالي
        exec_history = supabase.table('deep_execution_logs').select('execution_date, actual_minutes, focus_level, completed, deep_plans(deep_subjects(subject_name))').eq('user_id', user_id).execute()
        
        if exec_history.data:
            df_exec = pd.DataFrame(exec_history.data)
            
            # معالجة استخراج اسم المادة من الاستعلام المتداخل
            df_exec['المادة'] = df_exec['deep_plans'].apply(lambda x: x['deep_subjects']['subject_name'] if x and 'deep_subjects' in x and x['deep_subjects'] else 'أخرى')
            df_exec['الدقائق'] = df_exec['actual_minutes']
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                st.markdown('<div class="deep-card">', unsafe_allow_html=True)
                st.markdown("#### 🥧 إجمالي ساعات التركيز حسب المادة")
                subject_group = df_exec.groupby('المادة')['الدقائق'].sum().reset_index()
                subject_group['الساعات'] = subject_group['الدقائق'] / 60
                
                fig_subj = px.pie(subject_group, names='المادة', values='الساعات', hole=0.4, color_discrete_sequence=['#f0b429', '#238636', '#1f6feb', '#da3633'])
                fig_subj.update_layout(paper_bgcolor='#161b22', font_color='#e6edf3', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_subj, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_e2:
                st.markdown('<div class="deep-card">', unsafe_allow_html=True)
                st.markdown("#### 📈 تطور أداء التركيز عبر الأيام (بالدقائق)")
                date_group = df_exec.groupby('execution_date')['الدقائق'].sum().reset_index()
                
                fig_line = px.line(date_group, x='execution_date', y='الدقائق', markers=True, line_shape='spline', color_discrete_sequence=['#238636'])
                fig_line.update_layout(paper_bgcolor='#161b22', plot_bgcolor='#161b22', font_color='#e6edf3', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_line, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown('<div class="deep-card">', unsafe_allow_html=True)
            st.markdown("#### 🗂️ سجل جلسات التركيز المكتملة")
            st.dataframe(df_exec[['execution_date', 'المادة', 'الدقائق', 'focus_level', 'completed']], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("لا توجد سجلات جلسات منفذة حتى الآن لعرض الإحصائيات.")
    except Exception as ex:
        st.error(f"خطأ في جلب الإحصائيات: الخلل {ex}")
