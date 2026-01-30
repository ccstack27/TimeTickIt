# TimeTickIt

TimeTickIt is a lightweight and efficient time-tracking application designed to help you monitor your work sessions with ease. Whether you're a freelancer, a contractor, or just looking to manage your time better, TimeTickIt provides the tools you need to record your tasks and generate professional invoices and records.

## Features

- **Easy Tracking:** Start and stop sessions with a single click.
- **Task Management:** Assign specific tasks to each session.
- **Inactivity Detection:** Automatically ends sessions if no mouse or keyboard activity is detected for 5 minutes, ensuring your records stay accurate.
- **Account Records:** View your session history and accumulated work time directly in the app.
- **Invoice Generation:** Export your sessions into a professional package, including a generated invoice and administrative records.
- **Personalized Profile:** Customize your name, hourly rate, and choose from various fun avatars.

## How to Use

### 1. Setting Up Your Profile
- **Avatar:** Click on the avatar image on the left to cycle through different characters.
- **Name:** Enter your name in the "Name" field. This will be used in your generated invoices.
- **Hourly Rate:** Set your hourly rate in the "Rate" field.
- *Note: Your Name and Rate can only be edited when there is no active session and no unsaved records.*

### 2. Tracking a Session
- **Enter Task:** Type the name of the task you are working on in the "Task" field.
- **Start:** Click the **Start** button to begin tracking your time.
- **Monitor:** The app will display your current session start time and elapsed time.
- **Stop:** Click the **Stop** button when you are finished. Your session will be saved to your history.

### 3. Viewing Your Records
- Go to the **Account** menu and select **See Record**.
- A pop-up window will show your complete session history and the total accumulated time.

### 4. Generating an Invoice
- Click the **Generate Invoice** button at the bottom of the app.
- Choose a location to save the `.zip` package.
- This package contains your invoice and detailed records of all sessions tracked since your last export.
- *Note: Generating an invoice will clear your current session history in the app.*

### 5. Inactivity Protection
- If you step away from your computer for more than 5 minutes while a session is active, TimeTickIt will automatically stop the session and save it.
- A warning message will appear in the app when you have less than 3 minutes of inactivity remaining.

## Installation & Running

Ensure you have Python installed, then run the application using:

```bash
python main.py
```

---
Happy tracking with TimeTickIt!