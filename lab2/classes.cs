using System;
using System.Collections.Generic;
using System.Linq;


public class Hospital
{
    public string Name { get; set; }
    public string Address { get; set; }
    private List<Department> Departments { get; set; }

    public Hospital(string name, string address)
    {
        Name = name;
        Address = address;
        Departments = new List<Department>();
    }

    public void AddDepartment(Department dep)
    {
        Departments.Add(dep);
    }

    public List<Department> GetDepartments()
    {
        return Departments;
    }
}


public class Department
{
    public string Name { get; set; }
    private List<MedicalWorker> Staff { get; set; }

    public Department(string name)
    {
        Name = name;
        Staff = new List<MedicalWorker>();
    }

    public MedicalWorker AddStaff(string post)
    {
        // Реализация
    }

    public void RemoveStaff(MedicalWorker mw)
    {
        Staff.Remove(mw);
    }

    public List<MedicalWorker> GetStaff()
    {
        return Staff;
    }
}


public class Reception
{
    public string PhoneNumber { get; set; }
    private List<Appointment> Appointments { get; set; }

    public Reception(string phoneNumber)
    {
        PhoneNumber = phoneNumber;
        Appointments = new List<Appointment>();
    }

    public List<Appointment> ScheduleAppointment(Patient p, string complaints, DateTime datetime)
    {
        // Реализация
    }

    private Department ChooseDepartment(string complaints)
    {
        // Реализация
    }

    public void CancelAppointment(Appointment a, Patient p)
    {
        // Реализация
    }

    public void CreateMedicineCard(Patient p)
    {
        // Реализация
    }

    public MedicalCard GetMedicalCard(Patient p)
    {
        // Реализация
    }

    public List<Appointment> GetAppointments(Patient p)
    {
        // Реализация
    }
}


public class Patient
{
    public string Name { get; set; }
    public DateTime DateOfBirth { get; set; }
    public List<string> Complaints { get; set; }
    private List<Appointment> Appointments { get; set; }
    private MedicalCard Mc { get; set; }

    public Patient(string name, DateTime dateOfBirth)
    {
        Name = name;
        DateOfBirth = dateOfBirth;
        Complaints = new List<string>();
        Appointments = new List<Appointment>();
    }

    public List<string> GetComplaints()
    {
        return Complaints;
    }

    public void MakeAppointment(string complaints, List<DateTime> datetimes)
    {
        // Реализация
    }

    public void CameAppointment(Patient p)
    {
        // Реализация
    }
}


public class Appointment
{
    public DateTime Date { get; set; }
    public List<MedicalWorker> Staff { get; set; }
    public Patient Patient { get; set; }
    public MedicalCard Mc { get; set; }

    public Appointment(DateTime date, Patient patient)
    {
        Date = date;
        Patient = patient;
        Staff = new List<MedicalWorker>();
    }
}

public class MedicalWorker
{
    public string Name { get; set; }
    private TimeSheet WorkingHours { get; set; }

    public MedicalWorker(string name)
    {
        Name = name;
    }

    public void ScheduleAppointment(Appointment app)
    {
        // Реализация
    }

    public TimeSheet ShowWH()
    {
        return WorkingHours;
    }
}


public class Nurse : MedicalWorker
{
    public string Qualification { get; set; }

    public Nurse(string name, string qualification) : base(name)
    {
        Qualification = qualification;
    }

    public void AssistDoctor(MedicalWorker m)
    {
        // Реализация
    }

    public void TakeAnalysis(Patient p)
    {
        // Реализация
    }
}


public class Doctor : MedicalWorker
{
    public string Specialization { get; set; }

    public Doctor(string name, string specialization) : base(name)
    {
        Specialization = specialization;
    }

    public void ComplaintsAnalysis(List<string> complaints)
    {
        // Реализация
    }

    public void PatientCheckup(Patient p)
    {
        // Реализация
    }

    public void AddDiagnosis(MedicalCard medicalCard)
    {
        // Реализация
    }

    public void PrescribeTreatment(MedicalCard medicalCard)
    {
        // Реализация
    }
}


public class ScheduleEntry
{
    public MedicalWorker Worker { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public TimeSpan StartTime { get; set; }
    public TimeSpan EndTime { get; set; }
}


public class TimeSheet
{
    public List<ScheduleEntry> se { get; set; }

    public TimeSheet()
    {
        se = new List<ScheduleEntry>();
    }

    public void CreateSchedule(MedicalWorker m, DateTime startDate, DateTime endDate, TimeSpan startTime, TimeSpan endTime)
    {
        se.Add(new ScheduleEntry
        {
            Worker = m,
            StartDate = startDate,
            EndDate = endDate,
            StartTime = startTime,
            EndTime = endTime
        });
    }

    public void UpdateSchedule(MedicalWorker m, DateTime startDate, DateTime endDate, TimeSpan startTime, TimeSpan endTime)
    {
        var entry = se.FirstOrDefault(e => e.Worker == m && e.StartDate == startDate && e.EndDate == endDate);
        if (entry != null)
        {
            entry.StartTime = startTime;
            entry.EndTime = endTime;
        }
    }

    public void DeleteSchedule(MedicalWorker m, DateTime startDate, DateTime endDate)
    {
        var entry = se.FirstOrDefault(e => e.Worker == m && e.StartDate == startDate && e.EndDate == endDate);
        if (entry != null)
        {
            se.Remove(entry);
        }
    }

    public List<ScheduleEntry> getSchedule(MedicalWorker m)
    {
        return se.Where(e => e.Worker == m).ToList();
    }
}


public class MedicalCard
{
    public int Number { get; set; }
    public Patient Patient { get; set; }
    private List<Diagnosis> DiagnosisList { get; set; }

    public MedicalCard(int number, Patient patient)
    {
        Number = number;
        Patient = patient;
        DiagnosisList = new List<Diagnosis>();
    }

    public List<Diagnosis> GetPatientDiagnosis(Patient p)
    {
        return DiagnosisList;
    }

    public void UpdateDiagnosis(Diagnosis d)
    {
        // Реализация
    }
}


public class Diagnosis
{
    public string Description { get; set; }
    public DateTime DateDiagnosed { get; set; }
    public string Treatment { get; set; }
    private bool IsActive { get; set; }

    public Diagnosis(string description, DateTime dateDiagnosed, string treatment)
    {
        Description = description;
        DateDiagnosed = dateDiagnosed;
        Treatment = treatment;
        IsActive = true;
    }

    public bool GetStatus()
    {
        return IsActive;
    }

    public void UpdateTreatment(string newTreatment)
    {
        Treatment = newTreatment;
    }

    public void UpdateStatus(bool status)
    {
        IsActive = status;
    }
}