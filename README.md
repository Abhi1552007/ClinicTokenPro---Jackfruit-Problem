# ClinicTokenPro---Jackruit-Problem
Here’s a clean **README.md** for your appointment-booking program.
You can copy–paste this directly into a `README.md` file.

---

# 🏥 Hospital Appointment Booking System

A simple Python-based appointment booking system where patients select a speciality, choose a doctor from that speciality, and receive an automatic token number. Tokens are assigned **per doctor** in the order of bookings (1, 2, 3, ...).

---

## 📌 Features

* Fixed specialities with **3 doctors each**
* User selects:

  1. Speciality
  2. Doctor from that speciality
  3. Enters patient details
* Auto-generated token number **based on doctor’s previous appointments**
* Appointments saved to `appointments.txt` in table format
* Header added only once when file is created

---

## 🗂 File Created

```
appointments.txt
```

Example structure:

```
Name                Age  Speciality          Doctor              Date/Time           Token
--------------------------------------------------------------------------------------------
Rahul               25   Cardiology          Dr. Aarav Sharma    10:30 AM            1
Amit                40   Cardiology          Dr. Aarav Sharma    11:00 AM            2
Sneha               32   Dermatology         Dr. Riya Mehta      11:15 AM            1
```

---

## 🚀 How to Run

1. Make sure you have Python installed.
2. Save the `.py` script and this `README.md` in the same folder.
3. Run the program:

```bash
python appointment_system.py
```

---

## 🏷️ Current Specialities & Doctors

| Speciality  | Doctors                                              |
| ----------- | ---------------------------------------------------- |
| Cardiology  | Dr. Aarav Sharma, Dr. Diya Patel, Dr. Ishaan Rao     |
| Dermatology | Dr. Riya Mehta, Dr. Vivaan Iyer, Dr. Ananya Kulkarni |
| Orthopedics | Dr. Aditya Verma, Dr. Sara Reddy, Dr. Karan Joshi    |
| Neurology   | Dr. Neha Singh, Dr. Manav Nair, Dr. Kavya Pillai     |
| Pediatrics  | Dr. Saanvi Desai, Dr. Arjun Bhat, Dr. Meera Menon    |

---

## 🔢 Token Generation Logic

Tokens are assigned based on how many patients are already booked with the **same doctor**.

```
Token = (Number of previous appointments with that doctor) + 1
```

---

## 📄 Output Example

```
Available Specialities:
1. Cardiology
2. Dermatology
3. Orthopedics
4. Neurology
5. Pediatrics

Select a speciality (number): 1

Doctors for Cardiology:
1. Dr. Aarav Sharma
2. Dr. Diya Patel
3. Dr. Ishaan Rao
Select a doctor (number): 1

Enter patient details:
Name: Rahul
Age: 25
Date/Time: 10:30 AM

Appointment booked!
Doctor: Dr. Aarav Sharma
Speciality: Cardiology
Your token number is: 1
```

---

## 📍 Future Improvements (Optional)

* Separate tokens per date (reset daily)
* GUI / Tkinter interface
* Search patient by name or doctor
* Cancel / Edit appointment feature
* Export to Excel instead of text file

---

## 🧾 License

This project is free to use and modify for learning and development purposes.

---

