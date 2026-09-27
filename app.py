import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import datetime

# ==========================================
# 1. إعدادات الصفحة والواجهة الفاخرة
# ==========================================
st.set_page_config(page_title="Deep Work - نظام التركيز العميق", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19 !important; color: #f3f4f6 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, h4 { color: #38bdf8 !important; font-weight: 700 !important; }
    p, label, span, .stMarkdown { color: #94a3b8 !important; }
    
    .deep-card {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 14px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    input, textarea, select, div[data-baseweb="select"] > div { 
        background-color: #0f172a !important; 
        color: #f3f4f6 !important; 
        border: 1px solid #334155 !important; 
        border-radius: 8px !important; 
    }
    
    .stButton>button { 
        background-color: #0284c7 !important; 
        color: #ffffff !important; 
        border-radius: 8px !important; 
        border: none !important; 
        font-weight: bold !important; 
        padding: 10px 24px; 
    }
    .stButton>button:hover { background-color: #0369a1 !important; }
    
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
    hr { border-color: #1f2937 !important; }
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None

# ==========================================
# 3. شاشة الدخول والتسجيل
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 40px;'>🧠 Deep Work System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>منصة التخطيط الواعي والتركيز العميق الخالي من التشتت</p>", unsafe_allow_html=True)
        
        auth_tab = st.radio("اختر العملية", ["تسجيل الدخول", "إنشاء حساب جديد"], horizontal=True)
        
        if auth_tab == "تسجيل الدخول":
            with st.form("login_form"):
                mobile = st.text_input("رقم الموبايل")
                submit = st.form_submit_button("دخول للوحة العمل", use_container_width=True)
                
                if submit:
                    if mobile:
                        try:
                            res = supabase.table('deep_users').select('*').eq('mobile', mobile).execute()
                            if res.data:
                                user = res.data[0]
                                st.session_state.logged_in = True
                                st.session_state.user_id = user['id']
                                st.session_state.user_name = user['name']
                                st.rerun()
                            else:
                                st.error("رقم الموبايل غير مسجل.")
                        except Exception as ex:
                            st.error(f"خطأ: {ex}")
                    else:
                        st.warning("أدخل رقم الموبايل.")
        else:
            with st.form("reg_form"):
                name = st.text_input("الاسم الكريم")
                mobile = st.text_input("رقم الموبايل")
                submit_reg = st.form_submit_button("تسجيل حساب جديد", use_container_width=True)
                
                if submit_reg:
                    if name and mobile:
                        try:
                            res = supabase.table('deep_users').insert({'name': name, 'mobile': mobile}).execute()
                            if res.data:
                                user = res.data[0]
                                st.session_state.logged_in = True
                                st.session_state.user_id = user['id']
                                st.session_state.user_name = user['name']
                                st.success("تم إنشاء الحساب بنجاح!")
                                st.rerun()
                        except Exception as ex:
                            st.error("رقم الموبايل مسجل مسبقاً.")
                    else:
                        st.warning("أدخل الاسم ورقم الموبايل.")
    st.stop()

user_id = st.session_state.user_id
user_name = st.session_state.user_name

# ==========================================
# 4. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.markdown(f"### ⚡ أهلاً بك، {user_name}")
    st.markdown("---")
    app_mode = st.radio(
        "القائمة الرئيسية:",
        [
            "📚 إدارة المواد والمجالات", 
            "🗓️ التخطيط المسبق (خطة الغد)", 
            "⚡ تنفيذ وتقييم جلسات اليوم", 
            "📊 إحصائيات ومعدل الأداء"
        ]
    )
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

def convert_to_24h_time(h, m, period):
    if period == "مساءً (PM)" and h != 12:
        h += 12
    elif period == "صباحاً (AM)" and h == 12:
        h = 0
    return datetime.time(h, m)

# ==========================================
# القسم الأول: إدارة المواد
# ==========================================
if app_mode == "📚 إدارة المواد والمجالات":
    st.markdown("<h1>📚 إدارة المواد والمجالات الرئيسية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>حدد مجالات تركيزك الأساسية (برمجة، قراءة، لغات، إلخ).</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### ➕ إضافة مجال جديد")
        with st.form("subj_form"):
            s_name = st.text_input("اسم المجال أو المادة")
            s_desc = st.text_area("وصف الأهداف")
            if st.form_submit_button("حفظ المجال", use_container_width=True):
                if s_name:
                    supabase.table('deep_subjects').insert({'user_id': user_id, 'subject_name': s_name, 'description': s_desc}).execute()
                    st.success("تمت الإضافة بنجاح!")
                    st.rerun()
                else:
                    st.warning("أدخل اسم المجال.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### 📋 مجالاتك الحالية")
        try:
            subs = supabase.table('deep_subjects').select('*').eq('user_id', user_id).execute()
            if subs.data:
                st.dataframe(pd.DataFrame(subs.data)[['subject_name', 'description']], use_container_width=True)
            else:
                st.info("لا توجد مجالات مسجلة.")
        except:
            pass
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الثاني: التخطيط المسبق مع معالجة الأوقات بدقة
# ==========================================
elif app_mode == "🗓️ التخطيط المسبق (خطة الغد)":
    st.markdown("<h1>🗓️ التخطيط المسبق لجلسات التركيز</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>اختر وقت البدء والانتهاء بنظام 12 ساعة بكل مرونة وبدون أي تداخل في المواعيد.</p>", unsafe_allow_html=True)
    
    try:
        subs = supabase.table('deep_subjects').select('id, subject_name').eq('user_id', user_id).execute()
        s_dict = {s['subject_name']: s['id'] for s in subs.data} if subs.data else {}
    except:
        s_dict = {}
        
    if not s_dict:
        st.warning("⚠️ أضف مواد أو مجالات أولاً من قسم 'إدارة المواد والمجالات'.")
    else:
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        with st.form("plan_form"):
            c1, c2 = st.columns(2)
            p_date = c1.date_input("تاريخ الجلسة", datetime.date.today() + datetime.timedelta(days=1))
            chosen_s = c2.selectbox("المادة / المجال", options=list(s_dict.keys()))
            
            st.markdown("---")
            st.markdown("#### ⏰ وقت البدء")
            sc1, sc2, sc3 = st.columns(3)
            sh = sc1.selectbox("الساعة", list(range(1, 13)), index=10, key="sh") # افتراضي 11
            sm = sc2.selectbox("الدقيقة", [0, 15, 30, 45], key="sm")
            sp = sc3.selectbox("الفترة", ["صباحاً (AM)", "مساءً (PM)"], index=0, key="sp") # افتراضي صباحاً
            
            st.markdown("#### ⏰ وقت الانتهاء")
            ec1, ec2, ec3 = st.columns(3)
            eh = ec1.selectbox("الساعة", list(range(1, 13)), index=0, key="eh") # افتراضي 1
            em = ec2.selectbox("الدقيقة", [0, 15, 30, 45], index=0, key="em")
            ep = ec3.selectbox("الفترة", ["صباحاً (AM)", "مساءً (PM)"], index=1, key="ep") # افتراضي مساءً
            
            st.markdown("---")
            tasks = st.text_area("المهام المتوقع إنجازها في هذه الجلسة بالتفصيل")
            
            if st.form_submit_button("📅 اعتماد وجدولة الجلسة", use_container_width=True):
                if tasks:
                    new_start_t = convert_to_24h_time(sh, sm, sp)
                    new_end_t = convert_to_24h_time(eh, em, ep)
                    
                    if new_start_t >= new_end_t:
                        st.error("⚠️ خطأ في الوقت: وقت الانتهاء يجب أن يكون بعد وقت البدء.")
                    else:
                        try:
                            existing_plans = supabase.table('deep_plans').select('start_time, end_time').eq('user_id', user_id).eq('plan_date', str(p_date)).execute()
                            overlap = False
                            if existing_plans.data:
                                for ep_row in existing_plans.data:
                                    ex_start = datetime.datetime.strptime(str(ep_row['start_time']), "%H:%M:%S").time()
                                    ex_end = datetime.datetime.strptime(str(ep_row['end_time']), "%H:%M:%S").time()
                                    
                                    if (new_start_t < ex_end) and (new_end_t > ex_start):
                                        overlap = True
                                        break
                            
                            if overlap:
                                st.error("⚠️ عذراً، يوجد تداخل في الوقت مع جلسة أخرى مسجلة مسبقاً في نفس اليوم!")
                            else:
                                supabase.table('deep_plans').insert({
                                    'user_id': user_id,
                                    'plan_date': str(p_date),
                                    'subject_id': s_dict[chosen_s],
                                    'start_time': str(new_start_t),
                                    'end_time': str(new_end_t),
                                    'expected_tasks': tasks
                                }).execute()
                                st.success("🎉 تم جدولة الجلسة بنجاح وبدون أي تداخل!")
                                st.rerun()
                        except Exception as err:
                            st.error(f"خطأ أثناء التحقق أو الحفظ: {err}")
                else:
                    st.warning("اكتب المهام المتوقعة.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # جدول الخطط مع خيار الحذف
        st.markdown('<div class="deep-card">', unsafe_allow_html=True)
        st.markdown("### 📋 جدول خططك المستقبلية وإدارة الحذف")
        try:
            plans_res = supabase.table('deep_plans').select('id, plan_date, start_time, end_time, expected_tasks, deep_subjects(subject_name)').eq('user_id', user_id).gte('plan_date', str(datetime.date.today())).order('plan_date').execute()
            if plans_res.data:
                plans_list = plans_res.data
                df_p = pd.DataFrame(plans_list)
                st.dataframe(df_p[['plan_date', 'start_time', 'end_time', 'expected_tasks']], use_container_width=True)
                
                st.markdown("#### 🗑️ حذف جلسة مخططة")
                plan_options = {f"تاريخ: {p['plan_date']} | من {p['start_time']} لـ {p['end_time']} | المهام: {p['expected_tasks'][:30]}...": p['id'] for p in plans_list}
                
                chosen_to_delete = st.selectbox("اختر الجلسة المراد حذفها", options=list(plan_options.keys()))
                if st.button("🗑️ تأكيد حذف الجلسة المحددة", type="primary"):
                    target_id = plan_options[chosen_to_delete]
                    supabase.table('deep_plans').delete().eq('id', target_id).execute()
                    st.success("✅ تم حذف الجلسة بنجاح!")
                    st.rerun()
            else:
                st.info("لا توجد خطط مستقبلية مسجلة.")
        except Exception as e:
            st.error(f"خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الثالث: تنفيذ وتقييم اليوم
# ==========================================
elif app_mode == "⚡ تنفيذ وتقييم جلسات اليوم":
    st.markdown("<h1>⚡ تنفيذ وتقييم جلسات اليوم</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b;'>جلساتك المخططة لتاريخ اليوم: <b>{datetime.date.today()}</b>. سجل أداءك وتركيزك.</p>", unsafe_allow_html=True)
    
    today_str = str(datetime.date.today())
    try:
        today_plans = supabase.table('deep_plans').select('id, start_time, end_time, expected_tasks, deep_subjects(subject_name)').eq('user_id', user_id).eq('plan_date', today_str).execute()
        plans_list = today_plans.data if today_plans.data else []
    except:
        plans_list = []
        
    if not plans_list:
        st.info("📌 لا توجد جلسات مخططة لهذا اليوم. يمكنك التخطيط مسبقاً من قسم 'التخطيط المسبق'.")
    else:
        for idx, plan in enumerate(plans_list):
            st.markdown('<div class="deep-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🎯 جلسة #{idx+1}: {plan['deep_subjects']['subject_name']}")
            st.markdown(f"**الوقت المخطط:** من {plan['start_time']} إلى {plan['end_time']} | **المهام:** {plan['expected_tasks']}")
            
            try:
                exec_res = supabase.table('deep_execution_logs').select('*').eq('plan_id', plan['id']).execute()
                exec_data = exec_res.data[0] if exec_res.data else None
            except:
                exec_data = None
                
            with st.form(f"exec_{plan['id']}"):
                completed = st.checkbox("✅ هل أتممت هذه الجلسة؟", value=exec_data['completed'] if exec_data else False)
                focus_opts = ['تركيز عميق 100%', 'عالي', 'متوسط', 'مشتت / منخفض']
                f_idx = focus_opts.index(exec_data['focus_level']) if exec_data and exec_data['focus_level'] in focus_opts else 0
                focus = st.selectbox("🧠 مستوى التركيز الفعلي", focus_opts, index=f_idx)
                
                minutes = st.number_input("⏱️ الوقت الفعلي المستغرق (بالدقائق)", min_value=0, max_value=600, value=exec_data['actual_minutes'] if exec_data else 45)
                notes = st.text_area("📝 ملاحظات أو خواطر عن الجلسة", value=exec_data['notes'] if exec_data else "")
                
                if st.form_submit_button("💾 حفظ تقييم الجلسة", use_container_width=True):
                    payload = {
                        'user_id': user_id,
                        'plan_id': plan['id'],
                        'execution_date': today_str,
                        'completed': completed,
                        'focus_level': focus,
                        'actual_minutes': minutes,
                        'notes': notes
                    }
                    if exec_data:
                        supabase.table('deep_execution_logs').update(payload).eq('id', exec_data['id']).execute()
                        st.success("✅ تم تحديث التقييم بنجاح!")
                    else:
                        supabase.table('deep_execution_logs').insert(payload).execute()
                        st.success("🎉 أحسنت! تم حفظ إنجاز الجلسة.")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# القسم الرابع: الإحصائيات والأداء
# ==========================================
elif app_mode == "📊 إحصائيات ومعدل الأداء":
    st.markdown("<h1>📊 إحصائيات وتقارير معدل الأداء</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>تابع ساعات تركيزك العميق وتطور إنجازك عبر الرسوم البيانية الدقيقة.</p>", unsafe_allow_html=True)
    
    try:
        history = supabase.table('deep_execution_logs').select('execution_date, actual_minutes, focus_level, completed, deep_plans(deep_subjects(subject_name))').eq('user_id', user_id).execute()
        if history.data:
            df = pd.DataFrame(history.data)
            df['المادة'] = df['deep_plans'].apply(lambda x: x['deep_subjects']['subject_name'] if x and 'deep_subjects' in x and x['deep_subjects'] else 'أخرى')
            df['الدقائق'] = df['actual_minutes']
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="deep-card">', unsafe_allow_html=True)
                st.markdown("#### 🥧 ساعات التركيز حسب المادة")
                subj_grp = df.groupby('المادة')['الدقائق'].sum().reset_index()
                subj_grp['الساعات'] = subj_grp['الدقائق'] / 60
                fig_p = px.pie(subj_grp, names='المادة', values='الساعات', hole=0.4, color_discrete_sequence=['#38bdf8', '#0284c7', '#34d399', '#f43f5e'])
                fig_p.update_layout(paper_bgcolor='#111827', font_color='#f3f4f6', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_p, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c2:
                st.markdown('<div class="deep-card">', unsafe_allow_html=True)
                st.markdown("#### 📈 تطور أداء التركيز (بالدقائق)")
                date_grp = df.groupby('execution_date')['الدقائق'].sum().reset_index()
                fig_l = px.line(date_grp, x='execution_date', y='الدقائق', markers=True, line_shape='spline', color_discrete_sequence=['#38bdf8'])
                fig_l.update_layout(paper_bgcolor='#111827', plot_bgcolor='#111827', font_color='#f3f4f6', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_l, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown('<div class="deep-card">', unsafe_allow_html=True)
            st.markdown("#### 🗂️ سجل الجلسات المنفذة")
            st.dataframe(df[['execution_date', 'المادة', 'الدقائق', 'focus_level', 'completed']], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("لا توجد سجلات جلسات حتى الآن لعرض الإحصائيات.")
    except Exception as ex:
        st.error(f"خطأ في جلب الإحصائيات: {ex}")
