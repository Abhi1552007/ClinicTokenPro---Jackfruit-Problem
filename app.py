import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date, time as dtime, timedelta
import os

st.set_page_config(page_title="Clinic Token Pro", layout="wide")

TOKENS_FILE = "tokens.csv"
PATIENTS_FILE = "patients.csv"
SCHEDULE_FILE = "doctor_schedule.csv"
REPORTS_DIR = "reports"

HOSPITAL_USERS = {"hospital1": "pass123", "admin": "admin123"}

SPECIALITY_DOCTORS = {
    "Cardiology": ["Dr. Aarav Sharma", "Dr. Diya Patel", "Dr. Ishaan Rao"],
    "Dermatology": ["Dr. Riya Mehta", "Dr. Vivaan Iyer", "Dr. Ananya Kulkarni"],
    "Orthopedics": ["Dr. Aditya Verma", "Dr. Sara Reddy", "Dr. Karan Joshi"],
    "Neurology": ["Dr. Neha Singh", "Dr. Manav Nair", "Dr. Kavya Pillai"],
    "Pediatrics": ["Dr. Saanvi Desai", "Dr. Arjun Bhat", "Dr. Meera Menon"],
}

DEFAULT_DOCTOR_SCHEDULE = {
    "Dr. Aarav Sharma": ("09:00", "12:00"),
    "Dr. Diya Patel": ("09:00", "12:00"),
    "Dr. Ishaan Rao": ("09:00", "12:00"),
    "Dr. Riya Mehta": ("10:00", "13:00"),
    "Dr. Vivaan Iyer": ("10:00", "13:00"),
    "Dr. Ananya Kulkarni": ("10:00", "13:00"),
    "Dr. Aditya Verma": ("14:00", "17:00"),
    "Dr. Sara Reddy": ("14:00", "17:00"),
    "Dr. Karan Joshi": ("14:00", "17:00"),
    "Dr. Neha Singh": ("15:00", "18:00"),
    "Dr. Manav Nair": ("15:00", "18:00"),
    "Dr. Kavya Pillai": ("09:00", "12:00"),
    "Dr. Saanvi Desai": ("08:00", "11:00"),
    "Dr. Arjun Bhat": ("11:00", "14:00"),
    "Dr. Meera Menon": ("16:00", "19:00"),
}

SLOT_MINUTES = 15

TOKEN_COLUMNS = [
    "token_id","token_code","token_no",
    "patient_id","patient_name","age",
    "appointment_date","time_slot",
    "doctor","department","status","created_at"
]
PATIENT_COLUMNS = ["patient_id","name","age","phone"]
SCHEDULE_COLUMNS = ["doctor","start_time","end_time"]

def load_csv(path, cols):
    if os.path.exists(path):
        try: df = pd.read_csv(path)
        except: df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns: df[c] = ""
    return df[cols]

def save_csv(path, df):
    df.to_csv(path, index=False)

def load_tokens(): return load_csv(TOKENS_FILE, TOKEN_COLUMNS)
def save_tokens(df): save_csv(TOKENS_FILE, df)
def load_patients(): return load_csv(PATIENTS_FILE, PATIENT_COLUMNS)
def save_patients(df): save_csv(PATIENTS_FILE, df)

def get_all_doctors():
    return sorted({d for docs in SPECIALITY_DOCTORS.values() for d in docs})

def load_schedule():
    df = load_csv(SCHEDULE_FILE, SCHEDULE_COLUMNS)
    all_docs = get_all_doctors()
    rows = []
    for d in all_docs:
        r = df[df["doctor"] == d]
        if r.empty:
            start,end = DEFAULT_DOCTOR_SCHEDULE.get(d,("09:00","12:00"))
        else:
            start,end = str(r.iloc[0]["start_time"]),str(r.iloc[0]["end_time"])
        rows.append({"doctor":d,"start_time":start,"end_time":end})
    return pd.DataFrame(rows, columns=SCHEDULE_COLUMNS)

def save_schedule(df): save_csv(SCHEDULE_FILE, df)

def get_doctor_times(doctor, schedule_df):
    r = schedule_df[schedule_df["doctor"] == doctor]
    if r.empty: return None,None
    return str(r.iloc[0]["start_time"]),str(r.iloc[0]["end_time"])

def generate_slots(start_str, end_str, appt_date):
    sh,sm = map(int,start_str.split(":")); eh,em = map(int,end_str.split(":"))
    start_dt = datetime(appt_date.year,appt_date.month,appt_date.day,sh,sm)
    end_dt = datetime(appt_date.year,appt_date.month,appt_date.day,eh,em)
    slots,cur = [],start_dt
    while cur < end_dt:
        slots.append(cur)
        cur += timedelta(minutes=SLOT_MINUTES)
    return slots

def get_next_free_slot(doctor, appt_date, tokens_df, schedule_df):
    start_str,end_str = get_doctor_times(doctor, schedule_df)
    if not start_str or not end_str: return None
    today,now = date.today(),datetime.now()
    all_slots = generate_slots(start_str,end_str,appt_date)
    valid = [s for s in all_slots if appt_date > today or (appt_date == today and s >= now)]
    if not valid: return None
    date_str = appt_date.strftime("%Y-%m-%d")
    mask = (tokens_df["doctor"]==doctor)&(tokens_df["appointment_date"]==date_str)
    taken = set()
    for ts in tokens_df.loc[mask,"time_slot"]:
        if isinstance(ts,str) and ":" in ts:
            h,m = map(int,ts.split(":")); taken.add(dtime(h,m))
    for s in valid:
        if s.time() not in taken: return s
    return None

def get_next_token_no(doctor, appt_date, tokens_df):
    date_str = appt_date.strftime("%Y-%m-%d")
    mask = (tokens_df["doctor"]==doctor)&(tokens_df["appointment_date"]==date_str)
    return tokens_df.loc[mask].shape[0]+1

def format_time(dt_obj): return dt_obj.strftime("%I:%M %p")
def generate_patient_id(): return "P"+str(uuid.uuid4().int)[:6]

def find_patient_by_id(pid, patients_df):
    r = patients_df[patients_df["patient_id"]==pid]
    return None if r.empty else r.iloc[0]

for k,v in {
    "hospital_logged_in":False,
    "hospital_user":"",
    "loaded_patient":None,
    "pending_booking":None,
}.items():
    if k not in st.session_state: st.session_state[k]=v

st.title("Clinic Token System")
portal = st.radio("Select Portal",["Patient Portal","Hospital Portal"])

if portal=="Patient Portal":
    st.header("Patient Portal")
    patients_df = load_patients()

    st.subheader("Patient Login / Lookup (Patient ID)")
    c1,c2 = st.columns([2,1])
    with c1:
        pid_input = st.text_input("Enter your Patient ID (if already registered)")
    with c2:
        if st.button("Load Patient Details"):
            if not pid_input.strip():
                st.warning("Please enter a Patient ID.")
            else:
                row = find_patient_by_id(pid_input.strip(), patients_df)
                if row is None:
                    st.error("No patient found with this ID.")
                    st.session_state["loaded_patient"]=None
                else:
                    st.success(f"Patient found: {row['name']} (Age: {row['age']})")
                    st.session_state["loaded_patient"]=row.to_dict()

    st.subheader("New Patient Registration")
    r_name = st.text_input("Full Name")
    r_age = st.number_input("Age",0,120,25)
    r_phone = st.text_input("Phone Number")
    if st.button("Register New Patient"):
        if not r_name.strip():
            st.error("Name is required.")
        else:
            new_id = generate_patient_id()
            new_row = {"patient_id":new_id,"name":r_name.strip(),"age":int(r_age),"phone":r_phone.strip()}
            patients_df = pd.concat([patients_df,pd.DataFrame([new_row])],ignore_index=True)
            save_patients(patients_df)
            st.success(f"Registered! Your Patient ID is: {new_id}")
            st.info("Keep this ID for future bookings.")

    st.markdown("---")
    st.subheader("Book an Appointment")

    tokens_df = load_tokens()
    schedule_df = load_schedule()
    loaded = st.session_state["loaded_patient"]
    default_name = loaded["name"] if loaded is not None else ""
    default_age = int(loaded["age"]) if loaded and str(loaded["age"]).isdigit() else 25
    default_pid = loaded["patient_id"] if loaded is not None else ""

    if "patient_name_input" not in st.session_state: st.session_state["patient_name_input"]=default_name
    if "age_input" not in st.session_state: st.session_state["age_input"]=default_age
    if "patient_id_booking" not in st.session_state: st.session_state["patient_id_booking"]=default_pid
    if loaded is not None:
        st.session_state["patient_name_input"]=default_name
        st.session_state["age_input"]=default_age
        st.session_state["patient_id_booking"]=default_pid

    colA,colB = st.columns(2)
    with colA:
        pid_booking = st.text_input("Patient ID (optional for new patients)",key="patient_id_booking")
        p_name = st.text_input("Patient Name",key="patient_name_input")
        p_age = st.number_input("Age",0,120,key="age_input")
    with colB:
        dept = st.selectbox("Department",list(SPECIALITY_DOCTORS.keys()))
        doc = st.selectbox("Doctor",SPECIALITY_DOCTORS[dept])
        today = date.today()
        appt_date = st.date_input("Appointment Date",min_value=today)

    start_str,end_str = get_doctor_times(doc,schedule_df)
    if start_str and end_str:
        st.info(f"{doc} is available from {start_str} to {end_str} on the selected date.")
    else:
        st.warning("This doctor has no schedule defined.")

    st.markdown("_You will get the **next available 15-minute slot** in this window. First booking gets first slot, next booking gets the next, etc._")

    if st.button("Check Token Number and Expected Time"):
        if not p_name.strip():
            st.error("Please enter the patient name.")
        else:
            slot_dt = get_next_free_slot(doc,appt_date,tokens_df,schedule_df)
            if slot_dt is None:
                st.error("No available slots for this doctor on this date (or all remaining are in the past).")
            else:
                token_no = get_next_token_no(doc,appt_date,tokens_df)
                st.session_state["pending_booking"] = {
                    "token_id":str(uuid.uuid4())[:8],
                    "token_code":str(uuid.uuid4()).split("-")[0],
                    "token_no":token_no,
                    "patient_id":pid_booking.strip(),
                    "patient_name":p_name.strip(),
                    "age":int(p_age),
                    "appointment_date":appt_date.strftime("%Y-%m-%d"),
                    "time_slot":slot_dt.strftime("%H:%M"),
                    "doctor":doc,
                    "department":dept,
                    "status":"Pending",
                    "created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "expected_datetime_obj":slot_dt,
                }
                st.success("Slot found! Review below and confirm.")

    pending = st.session_state["pending_booking"]
    if pending is not None:
        st.markdown("---")
        st.subheader("Confirm Your Booking")
        exp_time = format_time(pending["expected_datetime_obj"])
        st.info(
            f"🧾 Token: **{pending['token_no']}**\n\n"
            f"👤 {pending['patient_name']} (Age: {pending['age']})\n\n"
            f"🩺 {pending['doctor']} ({pending['department']})\n\n"
            f"📅 {pending['appointment_date']}\n\n"
            f"⏰ Expected Call Time: **{exp_time}**\n\n"
            f"➡️ Please arrive **15–30 minutes earlier**."
        )
        if st.button("Confirm Booking"):
            new_row = {
                "token_id":pending["token_id"],
                "token_code":pending["token_code"],
                "token_no":pending["token_no"],
                "patient_id":pending["patient_id"],
                "patient_name":pending["patient_name"],
                "age":pending["age"],
                "appointment_date":pending["appointment_date"],
                "time_slot":pending["time_slot"],
                "doctor":pending["doctor"],
                "department":pending["department"],
                "status":pending["status"],
                "created_at":pending["created_at"],
            }
            tokens_df = load_tokens()
            tokens_df = pd.concat([tokens_df,pd.DataFrame([new_row])],ignore_index=True)
            save_tokens(tokens_df)
            st.success(f"✅ Booking confirmed! Token {pending['token_no']} for {pending['patient_name']} with {pending['doctor']} at {exp_time}.")
            st.session_state["pending_booking"]=None

else:
    st.header("Hospital Portal")
    if not st.session_state["hospital_logged_in"]:
        st.subheader("Hospital Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password",type="password")
        if st.button("Login"):
            if user in HOSPITAL_USERS and HOSPITAL_USERS[user]==pwd:
                st.session_state["hospital_logged_in"]=True
                st.session_state["hospital_user"]=user
                st.success(f"Logged in as {user}")
            else:
                st.error("Invalid username or password.")
    else:
        st.success(f"Logged in as {st.session_state['hospital_user']}")
        if st.button("Logout"):
            st.session_state["hospital_logged_in"]=False
            st.session_state["hospital_user"]=""
            st.experimental_rerun()

        st.markdown("---")
        tab_sched,tab_reports = st.tabs(["Doctor Schedule Management","Daily Token Reports"])

        with tab_sched:
            st.subheader("Edit Doctor Sitting Timings")
            sched_df = load_schedule()
            edited_sched = st.data_editor(sched_df,num_rows="fixed",use_container_width=True)
            if st.button("Save Schedule"):
                save_schedule(edited_sched)
                st.success("Schedule saved.")

        with tab_reports:
            st.subheader("Daily Token Reports")
            tokens_df = load_tokens()
            if tokens_df.empty:
                st.info("No tokens found yet.")
            else:
                rep_date = st.date_input("Select report date",value=date.today())
                all_docs = ["All"]+get_all_doctors()
                sel_doc = st.selectbox("Filter by Doctor",all_docs)
                ds = rep_date.strftime("%Y-%m-%d")
                mask = tokens_df["appointment_date"]==ds
                if sel_doc!="All": mask &= tokens_df["doctor"]==sel_doc
                rep_df = tokens_df[mask]
                st.write(f"Total tokens for {ds}: {len(rep_df)}")
                if rep_df.empty:
                    st.info("No tokens for this filter.")
                else:
                    edited_rep_df = st.data_editor(
                        rep_df,
                        num_rows="dynamic",
                        use_container_width=True,
                        column_config={
                            "status": st.column_config.SelectboxColumn(
                                "Status",options=["Pending","Completed","Cancelled"]
                            )
                        },
                        disabled=[c for c in rep_df.columns if c!="status"],
                    )
                    if st.button("Save Changes to Tokens"):
                        tokens_df.loc[mask,"status"]=edited_rep_df["status"].values
                        save_tokens(tokens_df)
                        st.success("Status updated successfully!")
                    if not edited_rep_df.empty:
                        csv_bytes = edited_rep_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download Report as CSV",
                            data=csv_bytes,
                            file_name=f"token_report_{ds}.csv",
                            mime="text/csv"
                        )
                        lines = [
                            f"Token {r.token_no} | {r.appointment_date} {r.time_slot} | {r.patient_name} (Age {r.age}) | {r.doctor} | Status: {r.status}"
                            for r in edited_rep_df.itertuples(index=False)
                        ]
                        report_text = "\n".join(lines)
                        os.makedirs(REPORTS_DIR,exist_ok=True)
                        txt_path = os.path.join(REPORTS_DIR,f"token_report_{ds}.txt")
                        with open(txt_path,"w",encoding="utf-8") as f:
                            f.write(report_text)
                        st.download_button(
                            "Download Report as TXT",
                            data=report_text.encode("utf-8"),
                            file_name=f"token_report_{ds}.txt",
                            mime="text/plain"
                        )
