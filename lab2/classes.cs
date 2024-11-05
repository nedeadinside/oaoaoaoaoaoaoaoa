using System;
using System.Collections.Generic;
using System.Linq;

public bool compute(var entry, List<DateTime> datetimes)
{
    // Заглушка функции, возвращающая значение по умолчанию
    return false;
}

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

    public void AddStaff(MedicalWorker mw)
    {
        Staff.Add(mw);
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

    public void ScheduleAppointment(Patient p, string complaints, List<DateTime> datetimes)
    {
        Department dep = ChooseDepartment(complaints);

        List<MedicalWorker> staff = dep.GetStaff();
        MedicalWorker selectedWorker = null;
        
        foreach (var worker in staff)
        {     
            var entry = worker.CheckAvailability(datetimes);
            if (entry != null)
            {
                selectedWorker = worker;
                
                Appointment a = new Appointment(p, entry, worker);
                
                Appointments.Add(a);

                worker.ShowWH().UpdateSchedule(entry, worker);
                break;
            }
        }
    }

    private Department ChooseDepartment(string complaints)
    {
        // Реализация выбора департамента на основе жалоб
        return null; // Заглушка
    }

    public void CancelAppointment(Appointment a, Patient p)
    {
        Appointments.Remove(a);
    }

    public void CreateMedicineCard(Patient p)
    {
        // Реализация
    }

    public MedicalCard GetMedicalCard(Patient p)
    {
        // Реализация
        return null; // Заглушка
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

    public void CameAppointment(Appointment a)
    {
        // Пациент вызывает жалобы у себя
        var complaints = GetComplaints();

        // Пациент из фильма Идиократия, поэтому он обращается к датаклассу appointment и только тогда понимает кто его доктор
        var doc = a.Staff;
        
        // Вызываем у доктора метод "обслужить" пациента 
        doc.schedulePatient(this, complaints, a)
    } 

    public List<string> GetComplaints()
    {
        return Complaints;
    }

    public void MakeAppointment(string complaints, List<DateTime> datetimes)
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

    public Appointment(Patient patient, DateTime date, MedicalWorker worker)
    {
        Date = date;
        Patient = patient;
        Staff = worker;
        Mc = patient.Mc;
    }
}

public class MedicalWorker
{
    public string Name { get; set; }
    private TimeSheet WorkingHours { get; set; }

    public MedicalWorker(string name)
    {
        Name = name;
        WorkingHours = new TimeSheet();
    }

    public void ScheduleAppointment(Appointment app)
    {
        // Реализация
    }

    public TimeSheet ShowWH()
    {
        return WorkingHours;
    }

    public ScheduleEntry CheckAvailability(List<DateTime> datetimes)
    {
        var timesheets = WorkingHours.getSchedule(this);
        foreach (var entry in timesheets)
        {
            if (compute(entry, datetimes))
            {
                return entry;
            }
        }
        return null;
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

    public string ComplaintsAnalysis(List<string> complaints)
    {
        // Реализация
        return "Analysis Result"; // Заглушка
    }

    public string PatientCheckup(Patient patient, List<Diagnosis> diagnosis, string complaintsAnalysisRes)
    {
        // Реализация
        return "New Treatment"; // Заглушка
    }

    public void AddDiagnosis(MedicalCard medicalCard)
    {
        // Реализация
    }

    public void PrescribeTreatment(MedicalCard medicalCard)
    {
        // Реализация
    }

    public void SchedulePatient(Patient patient, List<string> complaints, Appointment appointment)
    {
        var cm_res = this.ComplaintsAnalysis(complaints);

        var mc = appointment.Mc;
        
        var diagnosis = mc.GetPatientDiagnosis(); 

        var new_treatment = this.PatientCheckup(patient, diagnosis, cm_res);

        if (new_treatment != null)
        {
            mc.UpdateDiagnosis(diagnosis.First(), new_treatment);
        }
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

    public void CreateSchedule(MedicalWorker m, DateTime date)
    {
        // Реализация
    }

    public void UpdateSchedule(DateTime date, MedicalWorker m)
    {
        // Реализация
    }

    public void DeleteSchedule(MedicalWorker m, DateTime startDate, DateTime endDate)
    {
        // Реализация
    }

    public List<ScheduleEntry> getSchedule(MedicalWorker m)
    {
        // Реализация
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

    public List<Diagnosis> GetPatientDiagnosis()
    {
        return DiagnosisList;
    }

    public void UpdateDiagnosis(Diagnosis d, string treatment)
    {
        d.UpdateTreatment(treatment);
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
