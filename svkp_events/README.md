# 🎓 SVKP & Dr.K.S.Raju Arts & Science College
## Event Management System

A complete Django-based event management portal for college events including Sports, Cultural Activities, Academic, Technical events and more.

---

## 🚀 Features

### 👥 User Management
- **Three User Types**: Student, Staff, Other
- **OTP Verification**: Registration AND Login require OTP (shown in CMD/terminal)
- **Phone-based OTP**: 6-digit OTP displayed in server console
- **Separate registration pages** for Student, Staff, and Others

### 📅 Event Management
- Events: Sports 🏆, Cultural 🎭, Academic 📚, Technical 💻, Other 🌟
- **College-only events** restriction
- Staff/Admin can **Create and Update** events
- Event registration with seat management
- Event status: Upcoming, Ongoing, Completed, Cancelled

### 💳 Payment System
- **UPI Payment** with QR Code display (uploaded by staff)
- **Card/Net Banking** payment
- **Offline/Cash** payment option
- Payment QR codes managed by staff
- Transaction ID generation

### 🎫 Ticket Generation
- Unique ticket number (SVKP + 8 digits)
- Printable ticket with all event details
- Ticket status tracking

### 🔐 Admin Controls
- Staff & Admin can create/update events only
- QR code upload by staff
- Full Django admin panel

---

## 📦 Installation

### Step 1: Install Python & Dependencies
```bash
# Ensure Python 3.8+ is installed
python --version

# Install pip if not installed
# Then install requirements
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
cd svkp_events
python manage.py makemigrations accounts events payments
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
# Enter username, email, password
```

### Step 4: Create Sample Staff User (optional)
```bash
python manage.py shell
```
In shell:
```python
from accounts.models import CustomUser
staff = CustomUser.objects.create_user(
    username='staff1',
    password='staff123',
    first_name='College',
    last_name='Staff',
    email='staff@college.edu',
    phone='9999999999',
    user_type='staff',
    department='Administration',
    employee_id='EMP001',
    is_phone_verified=True
)
print("Staff created!")
exit()
```

### Step 5: Run the Server
```bash
python manage.py runserver
```

Open browser: **http://127.0.0.1:8000**

---

## 📱 OTP System

OTP is displayed in the **CMD/Terminal** where you run the Django server.

When user registers or logs in, look for this in terminal:
```
============================================================
  SVKP COLLEGE - OTP VERIFICATION
  Phone: 9876543210
  Purpose: REGISTRATION
  OTP Code: 456789
  Valid for: 10 minutes
============================================================
```

---

## 🔗 URL Structure

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/events/` | All events list |
| `/events/<id>/` | Event detail |
| `/events/<id>/register/` | Register for event |
| `/events/create/` | Create event (Staff only) |
| `/events/<id>/update/` | Update event (Staff only) |
| `/accounts/login/` | Login page |
| `/accounts/register/` | Registration choice |
| `/accounts/register/student/` | Student registration |
| `/accounts/register/staff/` | Staff registration |
| `/accounts/register/other/` | Other registration |
| `/accounts/register/verify-otp/` | OTP verification (registration) |
| `/accounts/login/verify-otp/` | OTP verification (login) |
| `/accounts/profile/` | User profile |
| `/payments/pay/<id>/` | Payment page |
| `/payments/ticket/<id>/` | View ticket |
| `/payments/qr-codes/` | QR Code management (Staff) |
| `/staff/dashboard/` | Staff dashboard |
| `/admin/` | Django admin |

---

## 🗄️ Database Schema

### Tables:
- **custom_users** - All user accounts (student/staff/other)
- **otp_verifications** - OTP records for verification
- **events** - College events
- **event_registrations** - User event registrations + ticket numbers
- **payments** - Payment records
- **payment_qr_codes** - QR code images uploaded by staff

---

## 🔑 Access Levels

| Action | Student | Staff | Admin |
|--------|---------|-------|-------|
| View Events | ✅ | ✅ | ✅ |
| Register for Events | ✅ | ✅ | ✅ |
| Create Events | ❌ | ✅ | ✅ |
| Update Events | ❌ | ✅ | ✅ |
| Upload QR Codes | ❌ | ✅ | ✅ |
| Staff Dashboard | ❌ | ✅ | ✅ |
| Django Admin | ❌ | ❌ | ✅ |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.8+ / Django 4.2+
- **Database**: SQLite (default) — can be changed to MySQL/PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Authentication**: Custom OTP-based auth
- **File Storage**: Local media files

---

## 📁 Project Structure

```
svkp_events/
├── manage.py
├── requirements.txt
├── README.md
├── svkp_events/           # Main Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/              # User management app
│   ├── models.py          # CustomUser, OTPVerification
│   ├── views.py           # Registration, Login, OTP views
│   ├── forms.py
│   └── urls.py
├── events/                # Events app
│   ├── models.py          # Event, EventRegistration
│   ├── views.py           # Event CRUD, registration
│   ├── forms.py
│   └── urls.py
├── payments/              # Payments app
│   ├── models.py          # Payment, PaymentQRCode
│   ├── views.py           # UPI, Card, Offline payment
│   ├── forms.py
│   └── urls.py
├── templates/             # HTML templates
│   ├── base/base.html
│   ├── events/
│   ├── accounts/
│   └── payments/
├── static/                # CSS, JS, Images
└── media/                 # Uploaded files
```

---

## 💡 Usage Guide

### For Students/Others:
1. Go to homepage
2. Click **Register** → Choose user type
3. Fill details → Submit → Enter OTP from terminal
4. Browse events → Click event → Register
5. Fill participant details → Go to payment
6. Choose UPI/Card/Offline → Complete payment
7. Download/Print ticket 🎫

### For Staff:
1. Register as Staff / Use admin credentials
2. Go to **Staff Dashboard**
3. Create events with all details
4. Upload QR codes for UPI/Card payments
5. Manage all events and registrations

### For Admin:
1. Login at `/admin/` with superuser credentials
2. Full control over all data
3. Can verify/confirm offline payments manually
