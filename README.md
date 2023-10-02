# All Inclusive HealthCare Portal
As in Covid-19 pandemic we have seen that quality HealthCare is one of the basic need of every person so, this project aims to provide quality healthcare to every person.
It solves the problems which we generally faced during pandemic like
* unable to take appointment with doctors without going hospitals.
* difficulty in finding Facilities like avialability of oxygen, beds, etc in hospitals.
* difficulty in finding vaccine slots in nearby hospitals.

Now this project provides solutions to above problems as
* user can can book appointment and chat with doctors.
* user can see facilities provided by hospitals without visiting anywhere.
* user can easily track their appointment requests.
* doctor and hospitals can manage appointment and vaccine bookings easily.

This project can be used by user or doctor or hospital.

A user can
* see and edit his/her details.
* search doctors based on their speciality and can chat and book appointment with them.
* search hospitals based on their location and book covid vaccines and see the facilities offered.
* see his/her appointment request status
* see his/her appointment history and rate the doctor after appointment.
* share thoughts on mental health portal and connect with our experts.

A hospital can
* see and edit all its details.
* add and update facilities offered like avialability of oxygen, blood, ambulance, covid-19 beds and different types of surgery.
* add timeslots for covid vaccines.
* see users coming for vaccine on a day.

A doctor can
* see and edit his/her details.
* add timeslots for appointments.
* accepts or rejects appointment requests.
* add post description or refer medicines to user after appointment.
* chat with users.

<h2>Contributers:-</h2>

 - Amit Kumar Makkad
 - Bhavya Contractor
 - Mihir karandikar
 - Priyansh Jaseja

This project is made as a part of course "Database and Information Systems" in Indian Institute of Technology, Indore.

## How to run
Clone the repo locally
```
git clone git@github.com:amitmakkad/G12_Healthcare.git
```
Now go to repo directory
```
cd G12_Healthcare/
```
Create a Virtual environment and activate it (for linux)
```
python -m venv myenv 
virtualenv myenv   
source myenv/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```

Create a .env file and add the following variable in the file
```
MYSQL_PASSWORD = <your_my_sql_password>
```

Go To Mysql
```
mysql -u root -p
USE cs207_healthcare_manangement;
```
If database not exists, create database using MySQL Scripts folder and set credentials in main.py <br><br>
Run the app
```
python main.py
```
