async function addEmployee(event){
    event.preventDefault();

    var employee = {
        'name': $('#employeenameinput').val(),
        'lastfour': $('#lastfourinput').val(),
    }

    if(employee.name.length === 0 || !employee.name.trim()){
        alert('please input employee name');
        return;
    }
    
    if(employee.lastfour.length !== 4 || isNaN(employee.lastfour) || isNaN(parseInt(employee.lastfour))){
        alert('please input valid SSN');
        return;
    }

    var enrollEmployeeResult = await fetch('add_employee',{
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
        },
        body: JSON.stringify(employee)
        });

        if(!enrollEmployeeResult.ok){
            throw Error(`Response status ${update_result.status}`);
        }
        clearEmployee();
        location.replace('/');

}

function clearEmployee(){
    $('#employeenameinput').val('');
    $('#lastfourinput').val('');
}