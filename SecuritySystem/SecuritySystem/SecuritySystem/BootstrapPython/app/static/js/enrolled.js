function getEmployee(event){
    var elements = event.target.parentNode.children;
    $('#employeenameinput').val(elements[0].innerText);
    $('#allowgeneralaccess').prop('checked',elements[1].innerText === "Yes");
    $('#allowweekendaccess').prop('checked',elements[2].innerText === "Yes");
    $('#allowafterhoursaccess').prop('checked',elements[3].innerText === "Yes");
}

function clearEmployee(event){
    if(event !== undefined){
        event.preventDefault();
    }
    $('#employeenameinput').val('');
    $('#allowgeneralaccess').prop('checked', false);
    $('#allowweekendaccess').prop('checked',false);
    $('#allowafterhoursaccess').prop('checked',false);
}



async function deleteEmployee(event) {
    event.preventDefault();
    var employeeName = $('#employeenameinput').val();
    if (employeeName !== '') {
        try {
            var response = await fetch('/delete_employee', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'name': employeeName })
            });

            if (!response.ok) {
                throw new Error(`Response status ${response.status}`);
            }

            var result = await response.json();
            alert(result.message);

            // Recargar la página después de la eliminación exitosa
            location.reload();
        } catch (error) {
            alert('Failed to delete employee: ' + error.message);
        }
    } else {
        alert('Please select an employee');
    }
}


async function addUpdateEmployee(event){
    event.preventDefault();
    var employee = {
        'name': $('#employeenameinput').val(),
        'general_access': $('#allowgeneralaccess').prop('checked'),
        'weekend_access': $('#allowweekendaccess').prop('checked'),
        'after_hours_access': $('#allowafterhoursaccess').prop('checked')
    }
    if(employee.name.length === 0 || !employee.name.trim()){
       alert('please input valid employee name');
       return;
    }

    var update_result = await fetch('update_employee',{
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
        },
        body: JSON.stringify(employee)
        });
    if(!update_result.ok){
        throw Error(`Response status ${update_result.status}`);
    }
    //get index of person. Otherwise add
    var enrolledEmployees = Array.from($('#enrolledemployeestablebody').children());
    var employeeToUpdate = enrolledEmployees.find((updateEmployee) => updateEmployee.children[0].innerText === employee.name);
    if(employeeToUpdate === undefined){
        //$('#enrolledemployeestablebody tr:last').after(`<tr onclick="getEmployee(event)"><td>${employee['name']}</td><td>${employee['general_access'] ? "Yes":"No"}</td><td>${employee['weekend_access'] ? "Yes":"No"}</td><td>${employee['after_hours_access'] ? "Yes":"No"}</td></tr>`);
        alert('no employee to update!')
    }else{
        employeeToUpdate.children[0].innerText = employee.name;
        employeeToUpdate.children[1].innerText = employee.general_access? "Yes":"No";
        employeeToUpdate.children[2].innerText = employee.weekend_access? "Yes":"No";
        employeeToUpdate.children[3].innerText = employee.after_hours_access? "Yes":"No";
    }
    clearEmployee();
}